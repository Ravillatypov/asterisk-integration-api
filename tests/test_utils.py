from app.asterisk.utils import get_internal, get_external, validate_numbers


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
