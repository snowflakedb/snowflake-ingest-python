from snowflake.ingest.utils import SecurityManager


def test_same_token(test_util):
    """
    Tests that accounts are parsed correctly
    """
    expected_account = 'TESTACCOUNT'

    actual_account = 'testaccount'
    user = 'testuser'
    private_key = ''
    sec_manager = SecurityManager(actual_account, user, private_key)
    assert sec_manager.get_account() == expected_account

    actual_account = 'testaccount.something'
    sec_manager = SecurityManager(actual_account, user, private_key)
    assert sec_manager.get_account() == expected_account
