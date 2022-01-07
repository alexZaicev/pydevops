import os
from abc import ABC

from lib.commands import REMOVE_TOOLS, CREATE_TOOLS, CHANGE_PERM_PYDEVOPS, TOOLS_SET_PASSWORD
from lib.config import ENV_PYDEVOPS_HOME, get_config_val, TM_USER, TM_PWD, DB_NAME, DB_PWD, DB_USER, DB_PORT, DB_HOST
from lib.model import TaskBase
from lib.ssh_client import SshClient


class Tool(TaskBase, ABC):

    def __init__(self, user, pwd):
        TaskBase.__init__(self)
        self.user = user
        self.client = SshClient(user, pwd)

        self.home_dir = self.get_home_dir()

    def run(self):
        self.pre_run()

    def close(self):
        self.client.close()

    def pre_run(self):
        self.client.execute_cmd(cmd=REMOVE_TOOLS)
        self.client.execute_cmd(cmd=CREATE_TOOLS)
        _p = os.path.join(os.getenv(ENV_PYDEVOPS_HOME, os.curdir), 'packages')
        for _f in os.listdir(_p):
            self.client.upload_file(os.path.join(_p, _f), '{}/pydevops/tools/{}'.format(self.home_dir, _f))
            self.client.execute_cmd(cmd='cd {}/pydevops/tools; tar -xzvf {}'.format(self.home_dir, _f))
            self.client.execute_cmd(cmd='cd {}/pydevops/tools; rm -f {}'.format(self.home_dir, _f))
        self.client.execute_cmd(cmd=CHANGE_PERM_PYDEVOPS)

    def get_home_dir(self):
        return self.client.execute_cmd(cmd='echo $FMP_HOME')


class DbTool(Tool, ABC):

    def __init__(self, user, pwd, dbHost, dbPort, dbUser, dbPwd, dbName):
        Tool.__init__(self, user=user, pwd=pwd)
        self.dbHost = dbHost
        self.dbPort = dbPort
        self.dbUser = dbUser
        self.dbPwd = dbPwd
        self.dbName = dbName


class SetPassword(DbTool):

    def __init__(self, org=None, pwd=None):
        DbTool.__init__(self, user=get_config_val(TM_USER), pwd=get_config_val(TM_PWD),
                        dbHost=get_config_val(DB_HOST),
                        dbPort=get_config_val(DB_PORT),
                        dbUser=get_config_val(DB_USER),
                        dbPwd=get_config_val(DB_PWD),
                        dbName=get_config_val(DB_NAME))
        self.org = org
        self.pwd = pwd

    def run(self):
        super().run()
        self.client.execute_cmd(
            cmd=TOOLS_SET_PASSWORD.format(self.home_dir, self.org, self.pwd, self.dbHost, self.dbPort, self.dbUser, self.dbPwd, self.dbName))
