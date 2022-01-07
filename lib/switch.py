import logging

from lib.commands import *
from lib.config import TM_USER, get_config_val, TM_PWD, SOLR_USER, SOLR_PWD, INGRES_USER, INGRES_PWD, ROOT_USER, ROOT_PWD, KEYCLOAK_AUTH_MODE, KEYCLOAK_USER
from lib.model import TaskBase
from lib.ssh_client import SshClient


class Switch(TaskBase):
    # OPERATIONS
    START = 'START'
    STOP = 'STOP'
    RESTART = 'RESTART'

    def __init__(self, op):
        TaskBase.__init__(self)
        self.op = op
        self.tm_client = SshClient(get_config_val(TM_USER), get_config_val(TM_PWD))
        self.solr_client = SshClient(get_config_val(SOLR_USER), get_config_val(SOLR_PWD))
        self.ing_client = SshClient(get_config_val(INGRES_USER), get_config_val(INGRES_PWD))
        self.root_client = SshClient(get_config_val(ROOT_USER), get_config_val(ROOT_PWD))

    def run(self):
        if self.op == Switch.RESTART:
            self._do_stop()
            self._do_start()
        elif self.op == Switch.START:
            self._do_start()
        else:
            self._do_stop()

    def close(self):
        self.tm_client.close()
        self.solr_client.close()
        self.ing_client.close()
        self.root_client.close()

    def _do_start(self):
        logging.getLogger(__name__).info("Starting Ingres DB...")
        self.ing_client.execute_cmd(cmd=START_INGRES)
        logging.getLogger(__name__).info("Ingres DB started...")

        logging.getLogger(__name__).info("Starting PostgreSQL...")
        self.root_client.execute_cmd(cmd=START_POSTGRES)
        logging.getLogger(__name__).info("PostgreSQL started...")

        if get_config_val(KEYCLOAK_AUTH_MODE):
            logging.getLogger(__name__).info("Starting KeyCloak...")
            self.root_client.execute_cmd(cmd=START_KEYCLOAK.format(get_config_val(KEYCLOAK_USER)))
            logging.getLogger(__name__).info("KeyCloak started...")

        logging.getLogger(__name__).info("Starting Solr Index...")
        self.solr_client.execute_cmd(cmd=START_SOLR)
        logging.getLogger(__name__).info("Solr Index started...")

        logging.getLogger(__name__).info("Starting TM...")
        self.tm_client.execute_cmd(cmd=START_TM)
        logging.getLogger(__name__).info("TM started...")

    def _do_stop(self):
        logging.getLogger(__name__).info("Stopping TM...")
        self.tm_client.execute_cmd(cmd=STOP_TM)
        logging.getLogger(__name__).info("TM stopped")

        logging.getLogger(__name__).info("Stopping Solr Index...")
        self.solr_client.execute_cmd(cmd=STOP_SOLR)
        logging.getLogger(__name__).info("Solr Index stopped...")

        if get_config_val(KEYCLOAK_AUTH_MODE):
            logging.getLogger(__name__).info("Stopping KeyCloak...")
            self.root_client.execute_cmd(cmd=STOP_KEYCLOAK.format(get_config_val(KEYCLOAK_USER)))
            logging.getLogger(__name__).info("KeyCloak stopped...")

        logging.getLogger(__name__).info("Stopping PostgreSQL...")
        self.root_client.execute_cmd(cmd=STOP_POSTGRES)
        logging.getLogger(__name__).info("PostgreSQL stopped...")

        logging.getLogger(__name__).info("Stopping Ingres DB...")
        self.ing_client.execute_cmd(cmd=STOP_INGRES)
        logging.getLogger(__name__).info("Ingres DB stopped...")
