from unittest import mock
from .. import ldapHelper

def test_escape():
    assert ldapHelper.escape("user1") == "user1"
    assert ldapHelper.escape("*") == r"\2a"
    assert ldapHelper.escape("a)(b") == r"a\29\28b"
    assert ldapHelper.escape("a\\b") == r"a\5cb"
    assert ldapHelper.escape(123) == "123"

@mock.patch("linuxmusterLinuxclient7.ldapHelper.searchOne")
def test_isObjectInGroupEscapesFilter(mockSearchOne):
    mockSearchOne.return_value = (True, {})
    assert ldapHelper.isObjectInGroup("cn=user,dc=x", "domain users)(cn=*")
    usedFilter = mockSearchOne.call_args.args[0]
    assert "*" not in usedFilter
    assert r"\2a" in usedFilter
