import math
import pytest

from amqp_data_types import *


def test_extract_octet():
    assert (2 ** 4, b'') == extract_octet(b'\x10')
    assert (2 ** 7, b'') == extract_octet(b'\x80')
    assert (2 ** 8 - 1, b'END') == extract_octet(b'\xffEND')


def test_extract_short_short_int():
    assert (2 ** 4, b'') == extract_short_short_int(b'\x10')
    assert (-2 ** 7, b'') == extract_short_short_int(b'\x80')
    assert (-1, b'END') == extract_short_short_int(b'\xffEND')


def test_extract_short_short_uint():
    assert (2 ** 4, b'') == extract_short_short_uint(b'\x10')
    assert (2 ** 7, b'') == extract_short_short_uint(b'\x80')
    assert (2 ** 8 - 1, b'END') == extract_short_short_uint(b'\xffEND')


def test_extract_boolean():
    assert (True, b'') == extract_boolean(b'\x01')
    assert (False, b'END') == extract_boolean(b'\x00END')


def test_extract_short_uint():
    assert (2 ** 8, b'') == extract_short_uint(b'\x01\x00')
    assert (2 ** 15, b'') == extract_short_uint(b'\x80\x00')
    assert (2 ** 16 - 1, b'END') == extract_short_uint(b'\xff\xffEND')


def test_extract_short_int():
    assert (2 ** 8, b'') == extract_short_int(b'\x01\x00')
    assert (-2 ** 15, b'') == extract_short_int(b'\x80\x00')
    assert (-1, b'END') == extract_short_int(b'\xff\xffEND')


def test_extract_long_uint():
    assert (2 ** 16, b'') == extract_long_uint(b'\x00\x01\x00\x00')
    assert (2 ** 31, b'') == extract_long_uint(b'\x80\x00\x00\x00')
    assert (2 ** 32 - 1, b'END') == extract_long_uint(b'\xff\xff\xff\xffEND')


def test_extract_long_int():
    assert (2 ** 16, b'') == extract_long_int(b'\x00\x01\x00\x00')
    assert (-2 ** 31, b'') == extract_long_int(b'\x80\x00\x00\x00')
    assert (-1, b'END') == extract_long_int(b'\xff\xff\xff\xffEND')


def test_extract_long_long_uint():
    assert (2 ** 32, b'') == extract_long_long_uint(b'\x00\x00\x00\x01\x00\x00\x00\x00')
    assert (2 ** 63, b'') == extract_long_long_uint(b'\x80\x00\x00\x00\x00\x00\x00\x00')
    assert (2 ** 64 - 1, b'END') == extract_long_long_uint(b'\xff\xff\xff\xff\xff\xff\xff\xffEND')


def test_extract_long_long_int():
    assert (2 ** 32, b'') == extract_long_long_int(b'\x00\x00\x00\x01\x00\x00\x00\x00')
    assert (-2 ** 63, b'') == extract_long_long_int(b'\x80\x00\x00\x00\x00\x00\x00\x00')
    assert (-1, b'END') == extract_long_long_int(b'\xff\xff\xff\xff\xff\xff\xff\xffEND')


def test_extract_float():
    result, string_remainder = extract_float(b'\xff\xff\x12\x34')
    assert math.isnan(result)
    assert b'' == string_remainder
    assert (float('-inf'), b'') == extract_float(b'\xff\x80\x00\x00')
    assert (- (2 - 2 ** -23) * 2 ** 127, b'') == extract_float(b'\xff\x7f\xff\xff')
    assert (-1, b'') == extract_float(b'\xbf\x80\x00\x00')
    assert (-0.5, b'') == extract_float(b'\xbf\x00\x00\x00')
    assert (-2 ** (-149), b'') == extract_float(
        b'\x80\x00\x00\x01')  # denormalized number (exponent bits = -126)
    assert (0, b'END') == extract_float(b'\x00\x00\x00\x00END')
    assert (2 ** (-149), b'') == extract_float(
        b'\x00\x00\x00\x01')  # denormalized number (exponent bits = -126)
    assert (0.5, b'') == extract_float(b'\x3f\x00\x00\x00')
    assert (1, b'') == extract_float(b'\x3f\x80\x00\x00')
    assert ((2 - 2 ** -23) * 2 ** 127, b'') == extract_float(b'\x7f\x7f\xff\xff')
    assert (float('+inf'), b'') == extract_float(b'\x7f\x80\x00\x00')
    result, string_remainder = extract_float(b'\x7f\xff\x12\x34')
    assert math.isnan(result)
    assert b'' == string_remainder


def test_extract_double():
    result, string_remainder = extract_double(b'\xff\xf0\x12\x34\x56\x78\x9a\xbc')
    assert math.isnan(result)
    assert b'' == string_remainder
    assert (float('-inf'), b'') == extract_double(b'\xff\xf0\x00\x00\x00\x00\x00\x00')
    assert (- (2 - 2 ** -52) * 2 ** 1023, b'') == extract_double(
        b'\xff\xef\xff\xff\xff\xff\xff\xff')
    assert (-1, b'') == extract_double(b'\xbf\xf0\x00\x00\x00\x00\x00\x00')
    assert (-0.5, b'') == extract_double(b'\xbf\xe0\x00\x00\x00\x00\x00\x00')
    assert (-2 ** (-1074), b'') == extract_double(
        b'\x80\x00\x00\x00\x00\x00\x00\x01')  # denormalized number (exponent bits = -1022)
    assert (0, b'END') == extract_double(b'\x00\x00\x00\x00\x00\x00\x00\x00END')
    assert (2 ** (-1074), b'') == extract_double(
        b'\x00\x00\x00\x00\x00\x00\x00\x01')  # denormalized number (exponent bits = -1022)
    assert (0.5, b'') == extract_double(b'\x3f\xe0\x00\x00\x00\x00\x00\x00')
    assert (1, b'') == extract_double(b'\x3f\xf0\x00\x00\x00\x00\x00\x00')
    assert ((2.0 - 2 ** -52) * 2.0 ** 1023, b'') == extract_double(
        b'\x7f\xef\xff\xff\xff\xff\xff\xff')
    assert (float('+inf'), b'') == extract_double(b'\x7f\xf0\x00\x00\x00\x00\x00\x00')
    result, string_remainder = extract_double(b'\x7f\xf0\x12\x34\x56\x78\x9a\xbc')
    assert math.isnan(result)
    assert b'' == string_remainder


def test_extract_decimal():
    assert (6553.6, b'') == extract_decimal(b'\x01\x00\x01\x00\x00')
    assert (655.36, b'') == extract_decimal(b'\x02\x00\x01\x00\x00')


def test_extract_short_string():
    assert ('', b'') == extract_short_string(b'\x00')
    assert ('test', b'END') == extract_short_string(b'\x04testEND')


def test_extract_long_string():
    assert ('', b'') == extract_long_string(b'\x00\x00\x00\x00')
    assert ('test', b'END') == extract_long_string(b'\x00\x00\x00\x04testEND')


def test_extract_timestamp():
    assert ('1970-01-01 00:00:00.000000', b'END') == extract_timestamp(
        b'\x00\x00\x00\x00\x00\x00\x00\x00END')


def test_extract_field_array():
    assert ([1, True, "test"], b'END') == extract_field_array(
        b'\x00\x00\x00\x0D'
        b'i\x00\x00\x00\x01'
        b't\x01'
        b's\x04test'
        b'END')
    assert ([1, [2, 3, 4], 5], b'') == extract_field_array(
        b'\x00\x00\x00\x0F'
        b'b\x01'
        b'A\x00\x00\x00\x06b\x02b\x03b\x04'
        b'b\x05')


def test_extract_field_table():
    expected_dict = OrderedDict()
    expected_dict['key1'] = 1
    expected_dict['key2'] = 2
    assert (expected_dict, b'') == extract_field_table(
        b'\x00\x00\x00\x0e'
        b'\x04key1'
        b'b\x01'
        b'\x04key2b\x02')
    expected_dict = OrderedDict()
    expected_dict['key1'] = 1
    expected_dict['key2'] = OrderedDict({'key2.1': 2.1})
    expected_dict['key3'] = 3
    assert (expected_dict, b'END') == extract_field_table(
        b'\x00\x00\x00\x24'
        b'\x04key1b\x01\x04key2'
        b'F\x00\x00\x00\x0D\x06key2.1D\x01\x00\x00\x00\x15'
        b'\x04key3b\x03END')


def extract_void():
    assert ('', b'END') == extract_void(b'END')
