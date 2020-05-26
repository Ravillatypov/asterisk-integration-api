import pytest

from app.asterisk.data_types import CallNumbers
from app.asterisk.utils import get_internal, get_external, validate_numbers, get_call_type
from app.consts import CallType


def test_get_internal():
    assert get_internal('123') == '123'
    assert get_internal('123d') == '123'
    assert get_internal('aertd') == ''
    assert get_internal('12345323') == ''


def test_get_external():
    assert get_external('123123123') == '123123123'
    assert get_external('123123') == '123123'
    assert get_external('1232') == ''
    assert get_external('asdfasdf12321234') == '12321234'


def test_validate_non_numbers():
    num = validate_numbers('wmgsgb', 'sdfsdgn')
    assert num.from_pin == ''
    assert num.from_number == ''
    assert num.request_pin == ''
    assert num.request_number == ''
    assert bool(num) == False


def test_validate_equal_numbers():
    num = validate_numbers('123', '123')
    assert num.from_pin == '123'
    assert num.from_number == ''
    assert num.request_pin == '123'
    assert num.request_number == ''
    assert bool(num) == False


def test_validate_numbers():
    num = validate_numbers('123', '72346754')
    assert num.from_pin == '123'
    assert num.from_number == ''
    assert num.request_pin == ''
    assert num.request_number == '72346754'
    assert bool(num) == True


@pytest.mark.parametrize('from_pin,from_num,req_num,req_pin,call_type', [
    ('', '', '', '', CallType.UNKNOWN),
    ('', '546432', '9954563', '', CallType.UNKNOWN),
    ('', '8644423', '', '439', CallType.INCOMING),
    ('423', '', '', '439', CallType.INTERNAL),
    ('423', '', '5456456', '', CallType.OUTBOUND),
])
def test_get_call_type(from_pin, from_num, req_num, req_pin, call_type):
    num = CallNumbers(from_pin, from_num, req_num, req_pin)
    assert get_call_type(num) == call_type
