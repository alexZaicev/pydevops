from abc import ABC

from lib.artifact_downloader import ArtifactDownloader
from lib.commands import *
from lib.config import *
from lib.model import TaskBase, parse_version
from lib.ssh_client import SshClient


class UpgraderBase(TaskBase, ABC):

    def __init__(self, repoUrl=None, version=None, user=None, pwd=None):
        TaskBase.__init__(self)
        self.repoUrl = repoUrl
        self.version = parse_version(version)

        self.user = user
        self.client = SshClient(user=user, pwd=pwd)

        self.home_dir = self.get_home_dir()

    def get_home_dir(self):
        return self.client.execute_cmd(cmd='echo $HOME')


class WbUpgraderBase(UpgraderBase, ABC):

    def __init__(self, artifactPath, release=True, *args, **kwargs):
        UpgraderBase.__init__(self, repoUrl=get_config_val(REPO_HOST), *args, **kwargs)
        self.artifactPath = artifactPath
        self.release = release

    def close(self):
        self.client.close()

    def download_package(self):
        if self.release:
            self.repoUrl = '{}/{}/{}'.format(self.repoUrl, get_config_val(RELEASE_REPO), self.artifactPath)
        else:
            self.repoUrl = '{}/{}/{}'.format(self.repoUrl, get_config_val(SNAPSHOT_REPO), self.artifactPath)

        self.repoUrl, artifact_name = ArtifactDownloader.get_versioned_artifact_url(self.repoUrl, self.version)
        ArtifactDownloader.download_artifact(self.repoUrl,
                                             stream=True,
                                             file_path=os.path.join(get_config_val(TMP_DIR), artifact_name),
                                             artifact=artifact_name)
        return artifact_name

    @classmethod
    def transfer_old_config(cls, template_path, old_path, new_path):
        with open(template_path) as f1, open(old_path) as f2:
            f1_lines = f1.readlines()
            f2_lines = f2.readlines()
        dic1, dic2 = wb_config_to_dict(f1_lines), wb_config_to_dict(f2_lines)
        new_dic = dict()
        for key, val in dic1.items():
            if key.startswith('comment_'):
                new_dic[key] = val
            elif key in dic2:
                new_dic[key] = dic2[key]
            else:
                new_dic[key] = val

        with open(new_path, 'wb') as ff:
            for key, val in new_dic.items():
                if key.startswith('comment_'):
                    ff.write(val.encode())
                else:
                    ff.write('{}={}\n'.format(key, val).encode())


class WbIngresWbUpgrader(WbUpgraderBase):

    def __init__(self, *args, **kwargs):
        WbUpgraderBase.__init__(self, artifactPath='ch/bbp/fms/workbench.ingres', user=get_config_val(INGRES_USER), pwd=get_config_val(INGRES_PWD), *args,
                                **kwargs)

    def run(self):
        artifact = self.download_package()
        self.client.execute_cmd(cmd=STOP_INGRES)
        # backup current WB install
        self.client.execute_cmd(cmd=BACKUP_OLD_WB_INGRES)
        local_path = os.path.join(get_config_val(TMP_DIR), artifact)
        self.client.execute_cmd(cmd=CREATE_REPO)
        self.client.upload_file(local_path, '{}/repo/{}'.format(self.home_dir, artifact))
        # extract new WB
        self.client.execute_cmd(cmd=EXTRACT_WB_INGRES.format(artifact))
        # transfer ingres.config.example and old ingres.confg
        temp_file = os.path.join(get_config_val(TMP_DIR), 'ingres.config-template')
        old_file = os.path.join(get_config_val(TMP_DIR), 'ingres.config-old')
        new_file = os.path.join(get_config_val(TMP_DIR), 'ingres.config')
        self.client.download_file(temp_file, '{}/wb/ingres.config.example'.format(self.home_dir))
        self.client.download_file(old_file, '{}/wb-old/ingres.config'.format(self.home_dir))
        self.transfer_old_config(temp_file, old_file, new_file)
        self.client.upload_file(new_file, '{}/wb/ingres.config'.format(self.home_dir))

        # start tm
        self.client.execute_cmd(cmd=MAKE_CFG_INGRES)
        self.client.execute_cmd(cmd=START_INGRES)

        # clean up
        self.client.execute_cmd(cmd=DELETE_BACKED_UP_WB_INGRES)


class WbPostgresWbUpgrader(WbUpgraderBase):

    def __init__(self, *args, **kwargs):
        WbUpgraderBase.__init__(self, artifactPath='ch/bbp/fms/workbench.postgres', user=get_config_val(POSTGRES_USER), pwd=get_config_val(POSTGRES_PWD), *args,
                                **kwargs)

    def run(self):
        artifact = self.download_package()
        self.client.execute_cmd(cmd=STOP_POSTGRES)
        # backup current WB install
        self.client.execute_cmd(cmd=BACKUP_OLD_WB_POSTGRES)
        local_path = os.path.join(get_config_val(TMP_DIR), artifact)
        self.client.execute_cmd(cmd=CREATE_REPO)
        self.client.upload_file(local_path, '{}/repo/{}'.format(self.home_dir, artifact))
        # extract new WB
        self.client.execute_cmd(cmd=EXTRACT_WB_POSTGRES.format(artifact))
        # transfer fmp.config.example and old fmp.confg
        temp_file = os.path.join(get_config_val(TMP_DIR), 'fmp.config-template')
        old_file = os.path.join(get_config_val(TMP_DIR), 'fmp.config-old')
        new_file = os.path.join(get_config_val(TMP_DIR), 'fmp.config')
        self.client.download_file(temp_file, '{}/wb/postgres.config.example'.format(self.home_dir))
        self.client.download_file(old_file, '{}/wb-old/postgres.config'.format(self.home_dir))
        self.transfer_old_config(temp_file, old_file, new_file)
        self.client.upload_file(new_file, '{}/wb/postgres.config'.format(self.home_dir))

        # start tm
        self.client.execute_cmd(cmd=MAKE_CFG_POSTGRES)
        self.client.execute_cmd(cmd=START_POSTGRES)

        # clean up
        self.client.execute_cmd(cmd=DELETE_BACKED_UP_WB_POSTGRES)


class WbSolrWbUpgrader(WbUpgraderBase):

    def __init__(self, *args, **kwargs):
        WbUpgraderBase.__init__(self, artifactPath='ch/bbp/fms/workbench.solr', user=get_config_val(SOLR_USER), pwd=get_config_val(SOLR_PWD), *args, **kwargs)

    def run(self):
        artifact = self.download_package()
        self.client.execute_cmd(cmd=STOP_SOLR)
        self.client.execute_cmd(cmd=BACKUP_OLD_WB_SOLR)
        local_path = os.path.join(get_config_val(TMP_DIR), artifact)
        self.client.execute_cmd(cmd=CREATE_REPO)
        self.client.upload_file(local_path, '{}/repo/{}'.format(self.home_dir, artifact))
        # extract new WB
        self.client.execute_cmd(cmd=EXTRACT_WB_SOLR.format(artifact))
        # transfer solr.config.example and old solr.confg
        temp_file = os.path.join(get_config_val(TMP_DIR), 'solr.config-template')
        old_file = os.path.join(get_config_val(TMP_DIR), 'solr.config-old')
        new_file = os.path.join(get_config_val(TMP_DIR), 'solr.config')
        self.client.download_file(temp_file, '{}/wb/solr.config.example'.format(self.home_dir))
        self.client.download_file(old_file, '{}/wb-old/solr.config'.format(self.home_dir))
        self.transfer_old_config(temp_file, old_file, new_file)
        self.client.upload_file(new_file, '{}/wb/solr.config'.format(self.home_dir))

        # start tm
        self.client.execute_cmd(cmd=MAKE_CFG_SOLR)
        self.client.execute_cmd(cmd=DEPLOY_CFG_SOLR)
        self.client.execute_cmd(cmd=START_SOLR)

        self.client.execute_cmd(cmd=DELETE_BACKED_UP_WB_SOLR)


class WbTmWbUpgrader(WbUpgraderBase):

    def __init__(self, *args, **kwargs):
        WbUpgraderBase.__init__(self, artifactPath='ch/bbp/fms/workbench.tm', user=get_config_val(TM_USER), pwd=get_config_val(TM_PWD), *args, **kwargs)

    def get_home_dir(self):
        return self.client.execute_cmd(cmd='echo $FMP_HOME')

    def run(self):
        artifact = self.download_package()
        self.client.execute_cmd(cmd=STOP_TM)
        # backup current WB install
        self.client.execute_cmd(cmd=BACKUP_OLD_WB_TM)
        local_path = os.path.join(get_config_val(TMP_DIR), artifact)
        self.client.execute_cmd(cmd=CREATE_REPO)
        self.client.upload_file(local_path, '{}/repo/{}'.format(self.home_dir, artifact))
        # extract new WB
        self.client.execute_cmd(cmd=EXTRACT_TM_COMPONENT.format(artifact))
        # transfer fmp.config.example and old fmp.confg
        temp_file = os.path.join(get_config_val(TMP_DIR), 'fmp.config-template')
        old_file = os.path.join(get_config_val(TMP_DIR), 'fmp.config-old')
        new_file = os.path.join(get_config_val(TMP_DIR), 'fmp.config')
        self.client.download_file(temp_file, '{}/install/1_config/fmp.config.example'.format(self.home_dir))
        self.client.download_file(old_file, '{}/install-old/1_config/fmp.config'.format(self.home_dir))
        self.transfer_old_config(temp_file, old_file, new_file)
        self.client.upload_file(new_file, '{}/install/1_config/fmp.config'.format(self.home_dir))

        # start tm
        self.client.execute_cmd(cmd=MAKE_CFG_TM)
        self.client.execute_cmd(cmd=DEPLOY_CFG_TM)
        self.client.execute_cmd(cmd=START_TM)

        # clean up
        self.client.execute_cmd(cmd=DELETE_BACKED_UP_WB_TM)


class TomcatUpgrader(UpgraderBase):
    TOMCAT_CONF_FILES = [
        {'tomcat': 'tomcat.crt'},
        {'tomcat': 'tomcat.key.nopass'},
        {'truststore': 'truststore.ts'}
    ]

    def __init__(self, *args, **kwargs):
        UpgraderBase.__init__(self, user=get_config_val(TM_USER), pwd=get_config_val(TM_PWD), *args, **kwargs)

        self.repoUrl = 'https://archive.apache.org/dist/tomcat/tomcat-'
        if self.version is None:
            self.version = parse_version(get_config_val(DEFAULT_TOMCAT_VERSION))
        self.artifact_name = 'apache-tomcat-{}.tar.gz'.format(self.version)
        self.repoUrl = '{}{}/v{}/bin/{}'.format(self.repoUrl, self.version[:1], self.version, self.artifact_name)

        self.pki_client, self.root_client = None, None
        try:
            self.pki_client = SshClient(get_config_val(PKI_USER), get_config_val(PKI_PWD))
            self.root_client = SshClient(get_config_val(ROOT_USER), get_config_val(ROOT_PWD))
        except Exception:
            logging.getLogger(__name__).warning('PKI repo not configured on the connecting instance')

    def run(self):
        ArtifactDownloader.download_artifact(self.repoUrl,
                                             stream=True,
                                             file_path=os.path.join(get_config_val(TMP_DIR), self.artifact_name),
                                             artifact=self.artifact_name)
        self.client.execute_cmd(cmd=STOP_TM)
        # backup current tomcat install
        self.client.execute_cmd(cmd=BACKUP_OLD_TOMCAT)
        local_path = os.path.join(get_config_val(TMP_DIR), self.artifact_name)
        self.client.execute_cmd(cmd=CREATE_REPO)
        self.client.upload_file(local_path, '{}/repo/{}'.format(self.home_dir, self.artifact_name))
        self.client.execute_cmd(cmd=EXTRACT_TM_COMPONENT.format(self.artifact_name))
        # update symlink
        self.client.execute_cmd(cmd=REMOVE_TOMCAT_SYMLINK)
        self.client.execute_cmd(cmd=CREATE_TOMCAT_SYMLINK.format(self.artifact_name.replace('.tar.gz', '')))

        # transfer tomcat PKI files
        if self.pki_client is not None:
            pki_home = self.pki_client.execute_cmd(cmd='echo $HOME')
            self.root_client.execute_cmd(cmd='chmod -R 775 {}/ssl'.format(pki_home))
            for tf in TomcatUpgrader.TOMCAT_CONF_FILES:
                _d, _f = tuple(tf.keys())[0], tuple(tf.values())[0]

                _p = os.path.join(get_config_val(TMP_DIR), _f)
                self.pki_client.download_file(_p, '{}/ssl/{}/{}'.format(pki_home, _d, _f))
                self.client.upload_file(_p, '{}/tomcat/conf/{}'.format(self.home_dir, _f))

        # start tm
        self.client.execute_cmd(cmd=COPY_OLD_TOMCAT_WEBAPPS)
        self.client.execute_cmd(cmd=COPY_OLD_TOMCAT_LIBS)

        self.client.execute_cmd(cmd=MAKE_CFG_TM)
        self.client.execute_cmd(cmd=DEPLOY_CFG_TM)
        self.client.execute_cmd(cmd=START_TM)

        self.client.execute_cmd(cmd=DELETE_BACKED_UP_TOMCAT)

    def close(self):
        super().close()
        if self.pki_client is not None and self.root_client is not None:
            self.pki_client.close()
            self.root_client.close()


class JbossUpgrader(UpgraderBase):
    JBOSS_CONF_FILES = [
        {'wildfly': 'wildfly.jks'},
        {'truststore': 'truststore.ts'}
    ]

    def __init__(self, *args, **kwargs):
        UpgraderBase.__init__(self, user=get_config_val(TM_USER), pwd=get_config_val(TM_PWD), *args, **kwargs)

        if self.version is None:
            self.version = parse_version(get_config_val(DEFAULT_JBOSS_VERSION))
        self.artifact_name = 'wildfly-{}.Final.tar.gz'.format(self.version)
        self.repoUrl = 'https://download.jboss.org/wildfly/{}.Final/{}'.format(self.version, self.artifact_name)

        self.pki_client = SshClient(get_config_val(PKI_USER), get_config_val(PKI_PWD))
        self.root_client = SshClient(get_config_val(ROOT_USER), get_config_val(ROOT_PWD))

    def run(self):
        ArtifactDownloader.download_artifact(self.repoUrl,
                                             stream=True,
                                             file_path=os.path.join(get_config_val(TMP_DIR), self.artifact_name),
                                             artifact=self.artifact_name)
        self.client.execute_cmd(cmd=STOP_TM)
        # backup current tomcat install
        self.client.execute_cmd(cmd=BACKUP_OLD_JBOSS)
        local_path = os.path.join(get_config_val(TMP_DIR), self.artifact_name)
        self.client.execute_cmd(cmd=CREATE_REPO)
        self.client.upload_file(local_path, '{}/repo/{}'.format(self.home_dir, self.artifact_name))
        self.client.execute_cmd(cmd=EXTRACT_TM_COMPONENT.format(self.artifact_name))
        # update symlink
        self.client.execute_cmd(cmd=REMOVE_JBOSS_SYMLINK)
        self.client.execute_cmd(cmd=CREATE_JBOSS_SYMLINK.format(self.artifact_name.replace('.tar.gz', '')))

        # transfer tomcat PKI files
        pki_home = self.pki_client.execute_cmd(cmd='echo $HOME')
        self.root_client.execute_cmd(cmd='chmod -R 775 {}/ssl'.format(pki_home))
        for tf in JbossUpgrader.JBOSS_CONF_FILES:
            _d, _f = tuple(tf.keys())[0], tuple(tf.values())[0]

            _p = os.path.join(get_config_val(TMP_DIR), _f)
            self.pki_client.download_file(_p, '{}/ssl/{}/{}'.format(pki_home, _d, _f))
            self.client.upload_file(_p, '{}/jboss/standalone/configuration/{}'.format(self.home_dir, _f))

        # start tm
        self.client.execute_cmd(cmd=COPY_OLD_JBOSS_DEPLOYMENTS)
        self.client.execute_cmd(cmd=COPY_OLD_JBOSS_MODULES)
        self.client.execute_cmd(cmd=COPY_OLD_JBOSS_VAULT)

        self.client.execute_cmd(cmd=MAKE_CFG_TM)
        self.client.execute_cmd(cmd=DEPLOY_CFG_TM)
        self.client.execute_cmd(cmd=START_TM)

        self.client.execute_cmd(cmd=DELETE_BACKED_UP_JBOSS)

    def close(self):
        super().close()
        self.pki_client.close()
        self.root_client.close()
