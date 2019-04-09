import pytest
import spreadsheet_importer as si

def test_convert_value_str():
    assert isinstance(si.convert_value('Test String'), str)


def test_convert_value_int():
    converted_value = si.convert_value(4)
    assert isinstance(converted_value, str)
    assert converted_value == '4'


def test_convert_value_float():
    converted_value = si.convert_value(6.8)
    assert isinstance(converted_value, str)
    assert converted_value == '6.8'


def test_convert_value_float_trailing_zero():
    converted_value = si.convert_value(6.80)
    assert isinstance(converted_value, str)
    assert converted_value == '6.8'


def test_convert_value_int_trailing_zero():
    converted_value = si.convert_value(40)
    assert isinstance(converted_value, str)
    assert converted_value == '40'


