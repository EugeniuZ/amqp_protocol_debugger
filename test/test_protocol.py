import pytest


from amqp_protocol import _get_array_name


def test_array_name_conversion():
    assert "OPEN_CONNECTION" == _get_array_name("*open-connection")
    assert "OPEN_CONNECTION" == _get_array_name("?open-connection")
