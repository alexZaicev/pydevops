import os
import unittest

from lib.upgrader import WbTmWbUpgrader


class TestUpgrader(unittest.TestCase):

    def test_config_transfer(self):
        w = WbTmWbUpgrader()
        w.transfer_old_config(TestUpgrader.get_resource("fmp_config_template.config"), TestUpgrader.get_resource("fmp.config"),
                              TestUpgrader.get_resource("fmp.config.gen"))

    @staticmethod
    def get_resource(path):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(BASE_DIR, "test", "resource", path)
