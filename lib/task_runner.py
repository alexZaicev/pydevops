import logging
import os
import re
from argparse import ArgumentParser
from concurrent.futures.thread import ThreadPoolExecutor

from lib.artifact_downloader import ArtifactDownloader
from lib.config import ARTIFACTS, get_config_val, ROOT_DIR, TM_DEPLOY, KEYCLOAK_DEPLOY, get_release, TMP_DIR, PROJECT_TM, PROJECT_KC, REPO_HOST, RELEASE_REPO, \
    AUTH_MODE_KEYCLOAK, THREADS, AUTH_MODE_CAS, KEYCLOAK_AUTH_MODE
from lib.tools import SetPassword
from lib.deployer import TMDeployer, KeycloakDeployer
from lib.model import is_blank, UpgraderError
from lib.switch import Switch
from lib.upgrader import WbTmWbUpgrader, WbSolrWbUpgrader, WbIngresWbUpgrader, WbPostgresWbUpgrader, TomcatUpgrader, JbossUpgrader
from lib.xsd2xml import Xsd2Xml


class TaskRunner(object):
    TP_DEPLOY = 'taskDeploy'
    TP_SWITCH = 'taskSwitch'
    TP_UPGRADE = 'taskUpgrade'
    TP_XSD_2_XML = 'taskXsd2xml'
    TP_TOOLS = 'taskTools'

    def __init__(self):
        object.__init__(self)
        self._thread_pool = ThreadPoolExecutor(max_workers=get_config_val(THREADS))

    def run(self, task_type) -> bool:
        functionMap = {
            TaskRunner.TP_DEPLOY: self._deploy,
            TaskRunner.TP_SWITCH: self._switch,
            TaskRunner.TP_UPGRADE: self._upgrade,
            TaskRunner.TP_XSD_2_XML: self._xsd2xml,
            TaskRunner.TP_TOOLS: self._tools,
        }
        try:

            try:
                functionMap[task_type]()
            except KeyError:
                raise ValueError('Unknown task type [{}]'.format(task_type))

        except Exception as ex:
            logging.getLogger(__name__).error(str(ex))
            return False
        return True

    def _upgrade(self):
        parser = ArgumentParser()
        parser.add_argument('-wtm', '--workbench-tm', action='store_true', dest='wb_tm', default=False,
                            help='Upgrade TM workbench')
        parser.add_argument('-ws', '--workbench-solr', action='store_true', dest='wb_solr', default=False,
                            help='Upgrade Solr workbench')
        parser.add_argument('-wi', '--workbench-ingres', action='store_true', dest='wb_ing', default=False,
                            help='Upgrade Ingres workbench')
        parser.add_argument('-wpg', '--workbench-postgres', action='store_true', dest='wb_pg', default=False,
                            help='Upgrade Postgres workbench')
        parser.add_argument('-t', '--tomcat', action='store_true', dest='tomcat', default=False,
                            help='Upgrade Apache Tomcat')
        parser.add_argument('-j', '--jboss', action='store_true', dest='jboss', default=False,
                            help='Upgrade RedHat Jboss (WildFly)')
        parser.add_argument('-r', '--release', action='store_true', dest='release', default=False,
                            help='Upgrade to latest release')
        parser.add_argument('-v', '--version', action='store', dest='version', default=None, type=str,
                            help='Specific version of release/snapshot to fetch from artifactory')
        args = parser.parse_args()

        _upgrader = None
        if args.wb_tm:
            _upgrader = WbTmWbUpgrader(release=args.release, version=args.version)
        elif args.wb_solr:
            _upgrader = WbSolrWbUpgrader(release=args.release, version=args.version)
        elif args.wb_ing:
            _upgrader = WbIngresWbUpgrader(release=args.release, version=args.version)
        elif args.wb_pg:
            _upgrader = WbPostgresWbUpgrader(release=args.release, version=args.version)
        elif args.tomcat:
            _upgrader = TomcatUpgrader(version=args.version)
        elif args.jboss:
            _upgrader = JbossUpgrader(version=args.version)
        else:
            raise UpgraderError('Unsupported upgrade operation. Please check help page for more information')

        _upgrader.run()
        _upgrader.close()

    def _switch(self):
        parser = ArgumentParser()
        parser.add_argument('-s', '--start', action='store_true', dest='start', default=False,
                            help='Start VM services')
        parser.add_argument('-ss', '--stop', action='store_true', dest='stop', default=False,
                            help='Stop VM services')
        parser.add_argument('-r', '--restart', action='store_true', dest='restart', default=False,
                            help='Restart VM services')
        args = parser.parse_args()

        if args.restart:
            op = Switch.RESTART
        elif args.start:
            op = Switch.START
        else:
            op = Switch.STOP

        _switch = Switch(op)
        _switch.run()
        _switch.close()

    def _deploy(self):
        parser = ArgumentParser()
        parser.add_argument('-v', '--version', action='store', dest='version', default=None, type=str,
                            help='Version of TM/TS/TM4C to deploy (e.g. 6.0.4)')
        args = parser.parse_args()

        _auth_mode = None

        if is_blank(args.version):
            # load artifacts from local project build
            tm_arts, kc_arts = self._collect_local_artifacts()
        else:
            # deploy specific release artifacts collected from repository
            # tm_arts, kc_arts, _auth_mode = self._collect_repo_artifacts(self._thread_pool, args.version)
            tm_arts, kc_arts, _auth_mode = ['item'], [], AUTH_MODE_CAS

        deps = list()
        if get_config_val(TM_DEPLOY) and len(tm_arts) > 0:
            deps.append(TMDeployer(artifacts=tm_arts, auth_mode=_auth_mode))
        if get_config_val(KEYCLOAK_DEPLOY) and len(kc_arts) > 0 and _auth_mode == AUTH_MODE_KEYCLOAK:
            deps.append(KeycloakDeployer(artifacts=kc_arts))

        for dep in deps:
            dep.run()
            dep.close()

    def _xsd2xml(self):
        parser = ArgumentParser()
        parser.add_argument('-xsd', action='store', dest='xsd', help='XSD schemas input directory')
        parser.add_argument('-xml', action='store', dest='xml', help='Generated XML output directory')
        parser.add_argument('-o', '--optional', action='store_true', dest='opts', default=False, help='Generated optional attributes')
        parser.add_argument('-v', '--validate', action='store_true', dest='validate', default=False, help='Validate generated XML')

        args = parser.parse_args()

        xsd2xml = Xsd2Xml(dir_xsd=args.xsd, dir_xml=args.xml, optional=args.opts, validate=args.validate)
        xsd2xml.run()
        xsd2xml.close()

    def _tools(self):
        parser = ArgumentParser()
        parser.add_argument('--set-password', action='store_true', dest='set_pwd', default=False, help='Set user password')
        parser.add_argument('-p', '--password', action='store', dest='pwd', type=str, help='Password to be set')
        parser.add_argument('-o', '--organization', action='store', dest='org', type=str, help='TM organization name')

        args = parser.parse_args()

        if args.set_pwd:
            dep = SetPassword(org=args.org, pwd=args.pwd)
            dep.run()
            dep.close()

    @classmethod
    def _collect_local_artifacts(cls):

        def _collect_deployables(deps, project):
            result = list()
            for a in deps:
                if str(a['project']).lower() == project.lower():
                    _dir = os.path.join(root_dir, a['path'])
                    for ff in os.listdir(_dir):
                        if re.match(a['regex'], ff):
                            a['path'] = os.path.join(_dir, ff)
                            result.append(a)
            return result

        root_dir = get_config_val(ROOT_DIR)
        arts = get_config_val(ARTIFACTS)
        dep_arts = list()
        for a in arts:
            if a['deploy']:
                if is_blank(a['name']) or is_blank(a['path']) or is_blank(a['regex']) \
                        or is_blank(a['project']) or is_blank(a['script']) \
                        or ('deployAfterStart' in a and a['deployAfterStart'] and is_blank(a['scriptAfterStart'])):
                    raise ValueError('Invalid artifact configuration')
                if a['name'] == 'keycloak-tomcat-root' and not get_config_val(KEYCLOAK_AUTH_MODE):
                    continue
                dep_arts.append(a)
        if len(dep_arts) == 0:
            return list(), list()
        return _collect_deployables(dep_arts, PROJECT_TM), _collect_deployables(dep_arts, PROJECT_KC)

    @classmethod
    def _collect_repo_artifacts(cls, thread_pool, version):
        tm_arts, kc_arts = list(), list()
        release_info = get_release(version)
        for release_art in release_info['artifact-versions']:
            thread_pool.submit(cls._start_download, release_art, tm_arts, kc_arts)
        thread_pool.shutdown()

        # check what authentication mode to use. If auth mode not provided, default to CAS
        if is_blank(release_info['authMode']) or AUTH_MODE_KEYCLOAK not in release_info['authMode']:
            kc_arts.clear()
            _authMode = AUTH_MODE_CAS
        else:
            _authMode = AUTH_MODE_KEYCLOAK
        return tm_arts, kc_arts, _authMode

    @classmethod
    def _start_download(cls, release_art, tm_arts, kc_arts):

        def _get_deployable_artifact(name):
            for _aa in get_config_val(ARTIFACTS):
                if re.match(_aa['regex'], name) and _aa['deploy']:
                    return _aa
            return None

        if release_art['version'].startswith('v'):
            release_art['version'] = release_art['version'][1:]
        artifact = '{}-{}.tar.gz'.format(release_art['name'], release_art['version'])
        url = '{}/{}/ch/bbp/fms/{}/{}'.format(get_config_val(REPO_HOST), get_config_val(RELEASE_REPO), release_art['name'], release_art['version'])
        url = '{}/{}'.format(url, artifact)

        _a = _get_deployable_artifact(artifact)
        if _a is not None:
            ArtifactDownloader.download_artifact(url, stream=True,
                                                 file_path=os.path.join(get_config_val(TMP_DIR), artifact),
                                                 artifact=artifact)
            _a['path'] = os.path.join(get_config_val(TMP_DIR), artifact)
            if _a['project'] == PROJECT_TM:
                tm_arts.append(_a)
            elif _a['project'] == PROJECT_KC:
                kc_arts.append(_a)
