import logging
import os
import shutil
from datetime import datetime

import yaml
from plyer import notification

ENV_PYDEVOPS_HOME = 'PYDEVOPS_HOME'
CFG_PYDEVOPS = 'pydevops.cfg'
CFG_RELEASES = 'release-management.yml'
TMP_DIR_NAME = '.pydevops'
CONFIG = None

PROJECT_TM = 'TM'
PROJECT_KC = 'KEYCLOAK'

AUTH_MODE_CAS = 'CAS'
AUTH_MODE_KEYCLOAK = 'KEYCLOAK'

"""
    CONFIG CONSTANTS
"""
LOG_DIR = 'logDir'
LOG_PREFIX = 'logPrefix'
LOG_LEVEL = 'logLevel'

ARTIFACTS = 'artifacts'
ROOT_DIR = 'rootDir'
TMP_DIR = 'tmpDir'
HOST = 'host'
PORT = 'port'

DB_HOST = "dbHost"
DB_PORT = "dbPort"
DB_USER = "dbUser"
DB_PWD = "dbPwd"
DB_NAME = "dbName"

TM_USER = 'tmUser'
TM_PWD = 'tmPwd'
KEYCLOAK_USER = 'kcUser'
KEYCLOAK_PWD = 'kcPwd'
ROOT_USER = 'rootUser'
ROOT_PWD = 'rootPwd'
SOLR_USER = 'solrUser'
SOLR_PWD = 'solrPwd'
INGRES_USER = 'ingUser'
INGRES_PWD = 'ingPwd'
POSTGRES_USER = 'pgUser'
POSTGRES_PWD = 'pgPwd'
PKI_USER = 'pkiUser'
PKI_PWD = 'pkiPwd'

REPO_USER = 'repoUser'
REPO_PWD = 'repoPwd'

KEYCLOAK_AUTH_MODE = 'isKeycloakConfiguredAsAuthMode'
KEYCLOAK_DEPLOY = 'keycloakDeploy'
TM_DEPLOY = 'tmDeploy'

RELEASE_REPO = 'releaseRepository'
SNAPSHOT_REPO = 'snapshotRepository'
REPO_HOST = 'repositoryHost'
THREADS = 'threads'

DEFAULT_TOMCAT_VERSION = 'defaultTomcatVersion'
DEFAULT_JBOSS_VERSION = 'defaultJbossVersion'

DEFAULT_TITLE_BAR = 'defaultTitleBar'
GENERATE_DEFAULT_TITLE_BAR = 'generateRandomTitleBar'


def init():
    _init_logger()
    _print_banner()
    _init_temp_dir()


def get_config():
    global CONFIG
    if CONFIG is not None:
        return CONFIG
    cfg_path = os.path.join(os.getenv(ENV_PYDEVOPS_HOME, os.curdir), CFG_PYDEVOPS)
    with open(cfg_path, 'r') as ff:
        CONFIG = yaml.load(ff, Loader=yaml.FullLoader)
    if CONFIG is None or len(CONFIG) == 0:
        raise ValueError('Invalid configuration file')
    if CONFIG[ARTIFACTS] is None or len(CONFIG[ARTIFACTS]) == 0:
        raise ValueError('Artifacts configuration not present')
    return CONFIG


def get_config_val(key):
    try:
        return get_config()[key]
    except KeyError:
        logging.getLogger(__name__).error("[{}] config not found".format(key))
        return None


def show_notification(msg):
    notification.notify(
        title="PyDevOps",
        message=msg,
        toast=True,
        timeout=3
    )


def get_release(version: str):
    if not version.startswith('v'):
        version = 'v{}'.format(version)
    # load release mgmt file
    cfg_path = os.path.join(os.curdir, CFG_RELEASES)
    with open(cfg_path, 'r') as ff:
        _data = yaml.load(ff, Loader=yaml.FullLoader)
    if _data is None or len(_data) == 0:
        raise ValueError('Release management specification is emtpy')
    for _r in _data:
        if _r['version'] == version:
            return _r
    raise ValueError('Version {} not specified in release management specification'.format(version))


def wb_config_to_dict(lines: list):
    _cid = 0
    d = dict()
    for _l in lines:
        if str.startswith(_l, '#') or _l == '\n' or _l.replace(' ', '').startswith('#'):
            d['comment_{}'.format(_cid)] = _l
            _cid += 1
            continue
        t = list()
        for i in range(0, len(_l), 1):
            c = _l[i]
            if c == '=':
                t.append(_l[0: i])
                t.append(_l[i + 1:])
                break
        d[t[0]] = t[1].replace('\n', '')
    return d


def _init_temp_dir():
    cfg = get_config()
    _path = os.path.join(os.path.expanduser('~'), TMP_DIR_NAME)
    if not os.path.exists(_path):
        os.mkdir(_path)
    else:
        shutil.rmtree(_path)
        os.mkdir(_path)

    cfg[TMP_DIR] = _path


def _init_logger():
    log_dir = get_config_val(LOG_DIR)
    prefix = get_config_val(LOG_PREFIX)
    log_level = get_config_val(LOG_LEVEL)

    now = datetime.now()
    timestamp = ('%04d%02d%02d%02d%02d%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second))
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    else:
        file_dict = dict()
        log_files = [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]
        for lf in log_files:
            if lf.startswith(prefix):
                ts = int(lf.replace(prefix, '').replace('_', '').replace('.log', ''))
                file_dict[ts] = lf
        keys = sorted(file_dict, reverse=True)
        if len(keys) > 9:
            i = 0
            for k in keys:
                if i >= 9:
                    os.remove(os.path.join(log_dir, file_dict[k]))
                i += 1
    if prefix is None or len(prefix) == 0:
        log_name = '{}.log'.format(timestamp)
    else:
        log_name = '{}_{}.log'.format(prefix, timestamp)
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)-5.5s] [%(asctime)s] [%(filename)s - %(funcName)s] %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, log_name)),
            logging.StreamHandler()
        ]
    )


def _print_banner():
    logging.getLogger(__name__).info(
        """
                  ____        ____              ___            
                 |  _ \ _   _|  _ \  _____   __/ _ \ _ __  ___ 
                 | |_) | | | | | | |/ _ \ \ / / | | | '_ \/ __|
                 |  __/| |_| | |_| |  __/\ V /| |_| | |_) \__ \\
                 |_|    \__, |____/ \___| \_/  \___/| .__/|___/
                        |___/                       |_|        
        """)
