import struct

from collections import OrderedDict
from datetime import datetime


def extract_octet(value):
    assert len(value) >= 1
    return struct.unpack("B", value[:1])[0], value[1:]


def extract_short_short_int(value):
    assert len(value) >= 1
    return struct.unpack("b", value[:1])[0], value[1:]


def extract_short_short_uint(value):
    assert len(value) >= 1
    return struct.unpack("B", value[:1])[0], value[1:]


def extract_boolean(value):
    assert len(value) >= 1
    return struct.unpack("?", value[:1])[0], value[1:]


def extract_short_uint(value):
    assert len(value) >= 2
    return struct.unpack("!H", value[:2])[0], value[2:]


def extract_short_int(value):
    assert len(value) >= 2
    return struct.unpack("!h", value[:2])[0], value[2:]


def extract_long_uint(value):
    assert len(value) >= 4
    return struct.unpack("!L", value[:4])[0], value[4:]


def extract_long_int(value):
    assert len(value) >= 4
    return struct.unpack("!l", value[:4])[0], value[4:]


def extract_long_long_uint(value):
    assert len(value) >= 8
    return struct.unpack("!Q", value[:8])[0], value[8:]


def extract_long_long_int(value):
    assert len(value) >= 8
    return struct.unpack("!q", value[:8])[0], value[8:]


def extract_float(value):
    assert len(value) >= 4
    return struct.unpack("!f", value[:4])[0], value[4:]


def extract_double(value):
    assert len(value) >= 8
    return struct.unpack("!d", value[:8])[0], value[8:]


def extract_decimal(value):
    assert len(value) >= 5
    scale, value = extract_octet(value)
    result, value = extract_long_uint(value)
    decimal_result = float(result) / 10**scale
    return decimal_result, value


def extract_short_string(value):
    size, value = extract_octet(value)
    return struct.unpack("%ds" % size, value[:size])[0].decode('utf-8'), value[size:]


def extract_long_string(value):
    size, value = extract_long_uint(value)
    return struct.unpack("%ds" % size, value[:size])[0].decode('utf-8'), value[size:]


def extract_timestamp(value):
    assert len(value) >= 8
    timestamp = struct.unpack("!Q", value[:8])[0]
    return datetime.strftime(datetime.utcfromtimestamp(timestamp), '%Y-%m-%d %H:%M:%S.%f'), value[8:]


def extract_field_array(value):
    array_string_size, value = extract_long_uint(value)
    result = []
    array_bytes_processed = 0
    while array_bytes_processed < array_string_size:
        field_value_bytes_size = len(value)
        element_type, value = extract_octet(value)
        element, value = data_type_extraction_methods[chr(element_type)](value)
        field_value_bytes_size -= len(value)
        array_bytes_processed += field_value_bytes_size
        result.append(element)
    return result, value


def extract_field_table(value):
    table_string_size, value = extract_long_uint(value)
    result = OrderedDict()
    table_bytes_processed = 0
    while table_bytes_processed < table_string_size:
        field_value_pair_byte_size = len(value)
        field_name, value = extract_short_string(value)
        element_type, value = extract_octet(value)
        field_value, value = data_type_extraction_methods[chr(element_type)](value)
        field_value_pair_byte_size -= len(value)
        table_bytes_processed += field_value_pair_byte_size
        result[field_name] = field_value
    return result, value


def extract_void(value):
    return '', value



data_type_extraction_methods = {
    't': extract_boolean,
    'b': extract_short_short_int,
    'B': extract_short_short_uint,
    'U': extract_short_int,
    'u': extract_short_uint,
    'I': extract_long_int,
    'i': extract_long_uint,
    'L': extract_long_long_int,
    'l': extract_long_long_uint,
    'f': extract_float,
    'd': extract_double,
    'D': extract_decimal,
    's': extract_short_string,
    'S': extract_long_string,
    'A': extract_field_array,
    'T': extract_timestamp,
    'F': extract_field_table,
    'V': extract_void
}