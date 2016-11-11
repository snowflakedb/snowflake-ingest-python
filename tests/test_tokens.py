"""
test_tokens.py - This defines a series of tests to ascertain that we are
capable of renewing JWT tokens
"""

from unittest import TestCase
from snowflake.ingest.utils import SecurityManager
from datetime import timedelta
from time import sleep

#Tools for generating an RSA private key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)


class TestTokens(TestCase):
    """
    Handles testing whether or not the security manager
    renews tokens only after our set renewal period
    """
    def setUp(self):
        """
        Creates a security manager for the purposes of our tests
        """
        self.sec_man = SecurityManager("testaccount", "snowman", PRIVATE_KEY,
                                       renewal_delay=timedelta(seconds=3))
    def test_same_token(self):
        """
        Tests that we aren't immediately regenerating the key after each request
        """
        self.assertEqual(self.sec_man.get_token(), self.sec_man.get_token())

    def test_regenerate_token(self):
        """
        Tests that the security manager generates new tokens after we
        cross the set renewal threshold
        """
        old_token = self.sec_man.get_token()
        sleep(5)
        self.assertNotEqual(old_token, self.sec_man.get_token())


