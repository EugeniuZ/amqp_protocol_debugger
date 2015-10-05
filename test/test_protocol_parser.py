import pytest
import sys

from amqp_protocol_parser import *


def test_frame_extraction_from_empty_stream():
    parser = AMQPStreamParser(b'', "CLIENT")
    messages = []
    for message in parser:
        messages.append(message)
    assert [] == messages


def test_protocol_header_extraction():
    parser = AMQPStreamParser(b'AMQP\x00\x00\x09\x01', "CLIENT")
    messages = []
    for message in parser:
        messages.append(message)
    assert len(messages) == 1
    assert AMQPProtocolHeader(0, 0, 9, 1) == messages[0]


def test_single_frame_extraction():
    parser = AMQPStreamParser(b'\x01\x00\x00\x00\x00\x00\x0c\x00\x0a\x00\x1f\xff\xff\x00\x02\x00\x00\x00\x05\xce', "CLIENT")
    messages = []
    for message in parser:
        messages.append(message)
    assert len(messages) == 1
    assert AMQPFrame("CLIENT", 1, 0, b'\x00\x0a\x00\x1f\xff\xff\x00\x02\x00\x00\x00\x05') == messages[0]