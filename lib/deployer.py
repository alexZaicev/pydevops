import logging
import pyjokes

from abc import ABC, abstractmethod

from lib.commands import *
from lib.config import *
from lib.model import TaskBase
from lib.ssh_client import SshClient


class DeployerBase(TaskBase, ABC):

    def __init__(self, artifacts, user, pwd):
        TaskBase.__init__(self)
        self.artifacts = artifacts
        self.user = user
        self.client = SshClient(user, pwd)

        self.home_dir = self.get_home_dir()

    @abstractmethod
    def pre_deploy(self):
        pass

    @abstractmethod
    def get_home_dir(self):
        pass

    def run(self):
        self.pre_deploy()


class TMDeployer(DeployerBase):

    def __init__(self, auth_mode=None, *args, **kwargs):
        DeployerBase.__init__(self, user=get_config_val(TM_USER), pwd=get_config_val(TM_PWD), *args, **kwargs)
        self._auth_mode = auth_mode

    def pre_deploy(self):
        logging.getLogger(__name__).info("Preparing to deploy...")
        self.client.execute_cmd(cmd=REMOVE_SCRIPTS)
        self.client.execute_cmd(cmd=CREATE_SCRIPTS)
        _p = os.path.join(os.getenv(ENV_PYDEVOPS_HOME, os.curdir), 'scripts', 'tm')
        for _f in os.listdir(_p):
            self.client.upload_file(os.path.join(_p, _f), '{}/pydevops/scripts/{}'.format(self.home_dir, _f))
        self.client.execute_cmd(cmd=CHANGE_PERM_PYDEVOPS)

    def get_home_dir(self):
        return self.client.execute_cmd(cmd='echo $FMP_HOME')

    def run(self):
        super().run()
        logging.getLogger(__name__).info("Stopping TM...")
        self._stop_tm()
        logging.getLogger(__name__).info("TM stopped")

        new_config_value = dict()
        new_config_value['TITLE_BAR'] = '{}'.format(self._get_title_bar())

        if self._auth_mode is None:
            # if AUTH_MODE not set get from ENV
            _type = self.client.execute_cmd(ECHO_AUTH_TYPE)
            if _type == AUTH_MODE_KEYCLOAK:
                self._auth_mode = AUTH_MODE_KEYCLOAK
            else:
                self._auth_mode = AUTH_MODE_CAS
        else:
            # update AUTH_MODE in fmp.config to reflect correct release deployment
            if self._auth_mode is not None:
                logging.getLogger(__name__).info("Authentication mode configured [{}]".format(self._auth_mode))
                new_config_value['AUTHENTICATION_TYPE'] = self._auth_mode
        
        logging.getLogger(__name__).info("Updating TM configuraton...")
        self._update_config(new_config_value)

        logging.getLogger(__name__).info("Transferring artifacts..")
        self._transfer_artifacts()
        logging.getLogger(__name__).info("Deploying artifacts...")
        self._deploy_artifacts()
        logging.getLogger(__name__).info("Starting TM...")
        self._start_tm()
        logging.getLogger(__name__).info("TM started")
        logging.getLogger(__name__).info("Deploying artifacts after start...")
        self._deploy_artifacts_after_start()

    def _get_title_bar(self):
        if not get_config_val(GENERATE_DEFAULT_TITLE_BAR):
            return get_config_val(DEFAULT_TITLE_BAR)
        else:
            ss = pyjokes.get_joke(language="en", category="all")
            ss = ss.replace('n\'t', ' not')
            ss = ss.replace('\'s', 's')
            return ss

    def _update_config(self, values: dict):
        logging.getLogger(__name__).debug("Confguration values to be set: {}".format(values))

        local_path = os.path.join(get_config_val(TMP_DIR), 'fmp.config')
        self.client.download_file(local_path, '{}/install/1_config/fmp.config'.format(self.home_dir))
        with open(local_path) as ff:
            lines = ff.readlines()
        cfg_dict = wb_config_to_dict(lines)
        for key, value in values.items():
            if key in cfg_dict:
                start = 0
                # TITLE_BAR value may contain any character, so instead of parsing it
                # simply replace old with the new one
                if key == 'TITLE_BAR':
                    cfg_dict[key] = '"{}"'.format(value)
                    continue

                for _c in cfg_dict[key]:
                    if _c == ' ' or _c == '#':
                        break
                    start += 1
                cfg_dict[key] = cfg_dict[key][start:]
                cfg_dict[key] = '{} {}'.format(value, cfg_dict[key])
            else:
                logging.getLogger(__name__).error('Configuration tag [{}] does not exists in file [{}]'.format(key, local_path))

        new_path = os.path.join(get_config_val(TMP_DIR), 'fmp.config.tmp')
        with open(new_path, 'wb') as ff:
            for key, val in cfg_dict.items():
                if key.startswith('comment_'):
                    ff.write(val.encode())
                else:
                    ff.write('{}={}\n'.format(key, val).encode())
        self.client.upload_file(new_path, '{}/install/1_config/fmp.config'.format(self.home_dir))

        self.client.execute_cmd(cmd=MAKE_CFG_TM)
        self.client.execute_cmd(cmd=DEPLOY_CFG_TM)

    def close(self):
        self.client.close()

    def _stop_tm(self):
        self.client.execute_cmd(cmd=STOP_TM)
        logging.getLogger(__name__).info('TM killed successfully')

    def _start_tm(self):
        self.client.execute_cmd(cmd=START_TM)
        logging.getLogger(__name__).info('TM started successfully')

    def _transfer_artifacts(self):
        # prepare to transfer
        self.client.execute_cmd(cmd='chmod -R 744 {}/scripts'.format(self.home_dir))
        self.client.execute_cmd(cmd='{}/pydevops/scripts/clean_all'.format(self.home_dir))
        logging.getLogger(__name__).debug('Repository & deployment directories cleaned')

        # transfer
        for art in self.artifacts:
            rem_name = art['path'].split('\\')
            rem_name = rem_name[len(rem_name) - 1]
            self.client.upload_file(art['path'], '{}/repo/{}'.format(self.home_dir, rem_name))

    def _deploy_artifacts(self):
        for art in self.artifacts:
            rem_name = art['path'].split('\\')
            rem_name = rem_name[len(rem_name) - 1]
            self.client.execute_cmd(cmd='{}/pydevops/scripts/{} {}'.format(self.home_dir, art['script'], rem_name))
        self.client.execute_cmd(cmd='{}/pydevops/scripts/deploy_apps'.format(self.home_dir))
        self.client.execute_cmd(cmd='{}/pydevops/scripts/deploy_db'.format(self.home_dir))

    def _deploy_artifacts_after_start(self):
        for art in self.artifacts:
            if 'deployAfterStart' in art and art['deployAfterStart']:
                self.client.execute_cmd(cmd='{}/pydevops/scripts/{}'.format(self.home_dir, art['scriptAfterStart']))


class KeycloakDeployer(DeployerBase):

    def __init__(self, *args, **kwargs):
        DeployerBase.__init__(self, user=get_config_val(KEYCLOAK_USER), pwd=get_config_val(KEYCLOAK_PWD), *args, **kwargs)
        self.rootUser = get_config_val(ROOT_USER)
        self.rootClient = SshClient(get_config_val(ROOT_USER), get_config_val(ROOT_PWD))

    def pre_deploy(self):
        self.client.execute_cmd(cmd=REMOVE_SCRIPTS)
        self.client.execute_cmd(cmd=CREATE_SCRIPTS)
        _p = os.path.join(os.curdir, 'scripts', 'keycloak')
        for _f in os.listdir(_p):
            self.client.upload_file(os.path.join(_p, _f), '{}/pydevops/scripts/{}'.format(self.home_dir, _f))
        self.client.execute_cmd(cmd=CHANGE_PERM_PYDEVOPS)

    def get_home_dir(self):
        return self.client.execute_cmd(cmd='echo $HOME')

    def run(self):
        super().run()
        self._stop_keycloak()
        self._transfer_artifacts()
        self._deploy_artifacts()
        self._start_keycloak()

    def close(self):
        self.rootClient.close()
        self.client.close()

    def _stop_keycloak(self):
        self.rootClient.execute_cmd(cmd=STOP_KEYCLOAK.format(self.user))
        logging.getLogger(__name__).info('Keycloak has been stopped')

    def _start_keycloak(self):
        self.rootClient.execute_cmd(cmd=START_KEYCLOAK.format(self.user))
        logging.getLogger(__name__).info('Keycloak started successfully')

    def _transfer_artifacts(self):
        # prepare to transfer
        self.client.execute_cmd(cmd='chmod -R 744 {}/scripts'.format(self.home_dir))
        self.client.execute_cmd(cmd='{}/pydevops/scripts/clean_all'.format(self.home_dir))
        logging.getLogger(__name__).debug('Repository & deployment directories cleaned')

        # transfer
        for art in self.artifacts:
            rem_name = art['path'].split('\\')
            rem_name = rem_name[len(rem_name) - 1]
            self.client.upload_file(art['path'], '{}/repo/{}'.format(self.home_dir, rem_name))

    def _deploy_artifacts(self):
        art = self.artifacts[0]
        self.client.execute_cmd(cmd='{}/pydevops/scripts/{}'.format(self.home_dir, art['script']))
