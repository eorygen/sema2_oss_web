import os

from casper.tests import CasperTestCase


class SEMATestCase(CasperTestCase):

    def setUp(self):
        pass

    def test_create_program(self):
        """Test Create Program"""
        self.assertTrue(self.casper(os.path.join(os.path.dirname(__file__), 'jstests/test_create_program.js')))
