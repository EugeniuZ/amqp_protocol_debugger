import pytest
import struct
import sys
import threading
import time

import amqp_constants as const
import amqp_protocol_parser as parser

from amqp_protocol import _get_array_name, ProtocolDetective
from amqp_messages import AMQPProtocolHeader, AMQPFrame


def timeout(interval):
    def decorator(test_func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            result = []

            def test_func_thread(test_func, *args, **kwargs):
                try:
                    test_func(*args, **kwargs)
                except Exception as e:
                    result.append(e)
                finally:
                    result.append("done")

            test_timer = threading.Timer(interval, result.append, args=("interrupted",))
            test_thread = threading.Thread(target=test_func_thread,
                                           args=(test_func,) + args,
                                           kwargs=kwargs)
            test_thread.setDaemon(not sys.gettrace())  # in debug mode make thread blocking main
            test_thread.start()
            if not sys.gettrace():  # disable this in debug mode
                test_timer.start()
            while True:
                if test_thread.is_alive() and test_timer.is_alive():
                    time.sleep(0.1)
                else:
                    break

            if "interrupted" in result:
                raise Exception("%s did not finish in %s seconds" % (test_func.__name__,
                                                                     interval))
            else:
                test_timer.cancel()
                for test_result in result:
                    if test_result not in ["done", "interrupted"]:
                        raise test_result

        return wrapper

    return decorator


def _get_class_and_method(method_type):
    for class_id in const.AMQP_METHODS:
        for method_id in const.AMQP_METHODS[class_id]:
            if const.AMQP_METHODS[class_id][method_id] == method_type:
                return struct.pack("!HH", class_id, method_id)
    else:
        raise Exception("No such method: %s" % method_type)


def get_frame(source, method_type):
    if method_type == "BODY":
        return AMQPFrame(source, const.FRAME_BODY, 0, "")
    elif "HEADER" in method_type:
        return AMQPFrame(source, const.FRAME_HEADER, 0, struct.pack("!HHL", 10, 0, 0))
    elif "HEARTBEAT" in method_type:
        return AMQPFrame(source, const.FRAME_HEARTBEAT, 0, "")
    else:
        return AMQPFrame(source, const.FRAME_METHOD, 0, _get_class_and_method(method_type))


def make_messages(*messages):
    """Method accepts only atomic message specifications"""
    result = []
    for message in messages:
        participant, method_type = message.split(":")
        if participant == "C":
            if method_type == "protocol-header":
                result.append(AMQPProtocolHeader(0, 0, 0, 0))
            else:
                result.append(get_frame(parser.CLIENT, method_type))
        elif participant == "S":
            result.append(get_frame(parser.SERVER, method_type))
        else:
            raise ValueError("Invalid message spec: %s" % message)
    return result


def get_message(message):
    return make_messages(message)[0]


def test_array_name_conversion():
    assert "OPEN_CONNECTION" == _get_array_name("*open-connection")
    assert "OPEN_CONNECTION" == _get_array_name("?open-connection")


@timeout(1)
def test_atomic_rule_matching_SINGLE_CHALLENGE_EXCHANGE():
    client_messages = make_messages("C:connection.secure-ok")
    server_messages = make_messages("S:connection.secure")
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("challenge")
    result = protocol_analyzer.processed_messages

    assert len(result) == 2
    assert result == make_messages("S:connection.secure",
                                   "C:connection.secure-ok")
    assert all([not message.out_of_order for message in result])


@timeout(1)
def test_atomic_rule_matching_PUBLISH():
    client_messages = make_messages("C:basic.publish",
                                    "C:HEADER",
                                    "C:BODY")
    server_messages = []
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("publish")
    result = protocol_analyzer.processed_messages

    assert len(result) == 3
    assert result == make_messages("C:basic.publish",
                                   "C:HEADER",
                                   "C:BODY")
    assert all([not message.out_of_order for message in result])


@timeout(1)
def test_atomic_rule_matching_PUBLISH_with_acks():
    client_messages = make_messages("C:basic.publish",
                                    "C:HEADER",
                                    "C:BODY")
    server_messages = make_messages("S:basic.ack",
                                    "S:basic.ack",
                                    "S:basic.ack")

    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("publish")
    result = protocol_analyzer.processed_messages

    assert len(result) == 6
    assert result == make_messages("C:basic.publish", "S:basic.ack",
                                   "C:HEADER", "S:basic.ack",
                                   "C:BODY", "S:basic.ack")
    assert all([not message.out_of_order for message in result])


@timeout(1)
def test_atomic_rule_matching_DELIVER():
    client_messages = []
    server_messages = make_messages("S:basic.deliver",
                                    "S:BODY")
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("deliver")
    result = protocol_analyzer.processed_messages

    assert len(result) == 2
    assert result == make_messages("S:basic.deliver", "S:BODY")
    assert all([not message.out_of_order for message in result])


@timeout(1)
def test_alternative_rule_matching_CLOSE_CONNECTION():
    # test client initiated close
    client_messages = make_messages("C:connection.close")
    server_messages = make_messages("S:connection.close-ok")
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("close-connection")
    result = protocol_analyzer.processed_messages

    assert len(result) == 2
    assert result == make_messages("C:connection.close",
                                   "S:connection.close-ok")
    assert all([not message.out_of_order for message in result])

    # test server initiated close
    client_messages = make_messages("C:connection.close-ok")
    server_messages = make_messages("S:connection.close")
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("close-connection")
    result = protocol_analyzer.processed_messages

    assert len(result) == 2
    assert result == make_messages("S:connection.close",
                                   "C:connection.close-ok")
    assert all([not message.out_of_order for message in result])


@timeout(1)
def test_optional_rule_matching_OPEN_CLOSE_CONNECTION():
    client_messages = make_messages("C:protocol-header",
                                    "C:connection.start-ok",
                                    "C:connection.tune-ok",
                                    "C:connection.open",
                                    "C:connection.close")
    server_messages = make_messages("S:connection.start",
                                    "S:connection.tune",
                                    "S:connection.open-ok",
                                    "S:connection.close-ok")
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("protocol")
    result = protocol_analyzer.processed_messages

    assert len(result) == 9
    assert result == make_messages("C:protocol-header",
                                   "S:connection.start",
                                   "C:connection.start-ok",
                                   "S:connection.tune",
                                   "C:connection.tune-ok",
                                   "C:connection.open",
                                   "S:connection.open-ok",
                                   "C:connection.close",
                                   "S:connection.close-ok"
                                   )
    assert all([not message.out_of_order for message in result])


@timeout(2)
def test_repetitive_rule_matching_CHANNEL():
    client_messages = make_messages("C:channel.open",
                                    "C:channel.flow",
                                    "C:basic.consume",
                                    "C:basic.publish",
                                    "C:HEADER",
                                    "C:BODY",
                                    "C:basic.ack",
                                    "C:channel.close")
    server_messages = make_messages("S:channel.open-ok",
                                    "S:channel.flow-ok",
                                    "S:basic.consume-ok",
                                    "S:basic.ack",
                                    "S:basic.ack",
                                    "S:basic.ack",
                                    "S:channel.close-ok")

    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("channel")
    result = protocol_analyzer.processed_messages

    assert len(result) == 15
    assert result == make_messages("C:channel.open",
                                   "S:channel.open-ok",
                                   "C:channel.flow",
                                   "S:channel.flow-ok",
                                   "C:basic.consume",
                                   "S:basic.consume-ok",
                                   "C:basic.publish",
                                   "S:basic.ack",
                                   "C:HEADER",
                                   "S:basic.ack",
                                   "C:BODY",
                                   "S:basic.ack",
                                   "C:basic.ack",
                                   "C:channel.close",
                                   "S:channel.close-ok")
    assert all([not message.out_of_order for message in result])


@timeout(1)
def test_atomic_rule_matching_SINGLE_CHALLENGE_EXCHANGE_ignore_heartbeats():
    client_messages = make_messages("C:HEARTBEAT", "C:connection.secure-ok")
    server_messages = make_messages("S:HEARTBEAT", "S:connection.secure")
    protocol_analyzer = ProtocolDetective(client_messages, server_messages)

    protocol_analyzer._analyze_protocol_part("challenge")
    result = protocol_analyzer.processed_messages

    assert len(result) == 4
    for message in make_messages("S:HEARTBEAT",
                                 "C:HEARTBEAT",
                                 "S:connection.secure",
                                 "C:connection.secure-ok"):
        assert message in result  # heartbeat frames could be anywhere in between
    server_request = get_message("S:connection.secure")
    client_response = get_message("C:connection.secure-ok")
    assert result.index(server_request) < result.index(client_response), \
        "Server request should have been before client response: %s" % result
    assert all([not message.out_of_order for message in result])
