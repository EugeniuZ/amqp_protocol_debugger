import sys

from itertools import zip_longest

from amqp_protocol_spec import *


def _get_array_name(protocol_step):
    """Get one of the arrays from above given their name contained in a parent array"""
    protocol_step = protocol_step.replace("*", "").replace("?", "")  # strip quantifiers
    return protocol_step.upper().replace("-", "_")


def _is_client_step(step):
    return step.startswith("C:")


def _is_server_step(step):
    return step.startswith("S:")


def _is_repeatable_step_spec(step):
    return step.startswith("*")


def _is_optional_step_spec(step):
    return step.startswith("?")


def _is_alternative_step_spec(step):
    return " | " in step


def message_matches_step(step, message):
    return message.source.startswith(step[0]) and message.method == step[2:]


class ProtocolMismatch(Exception):
    pass


class ProtocolDetective(object):
    def __init__(self, client_messages, server_messages):
        self.processed_messages = []
        self.client_messages = client_messages
        self.server_messages = server_messages

    def analyze(self):
        try:
            self._analyze_protocol_part(PROTOCOL)
        except ProtocolMismatch:
            for client_message, server_message in zip_longest(self.client_messages, self.server_messages):
                if client_message:
                    client_message.out_of_order = True
                    self.processed_messages.append(client_message)
                if server_message:
                    server_message.out_of_order = True
                    self.processed_messages.append(server_message)
        return self.processed_messages

    def _analyze_protocol_part(self, protocol_table):
        int = 0
        for protocol_step in protocol_table:
            if _is_client_step(protocol_step):
                self._analyze_atomic_step(protocol_step, self.client_messages)
            elif _is_server_step(protocol_step):
                self._analyze_atomic_step(protocol_step, self.server_messages)
            elif _is_alternative_step_spec(protocol_step):
                protocol_alternatives = protocol_step.split(" | ")
                for protocol_alternative in protocol_alternatives:
                    if _is_optional_step_spec(protocol_alternative):
                        self._analyze_optional_step([protocol_alternative])
                    elif _is_repeatable_step_spec(protocol_alternative):
                        self._analyze_repeatable_step([protocol_alternative])
                    else:
                        protocol_part = getattr(sys.modules[__name__], _get_array_name(protocol_alternative))
                        try:
                            self._analyze_protocol_part(protocol_part)
                            break
                        except ProtocolMismatch:
                            pass  # the alternative did not match try the next one
                else:  # none of the alternatives matched
                    raise ProtocolMismatch
            elif _is_optional_step_spec(protocol_step):
                protocol_part = getattr(sys.modules[__name__], _get_array_name(protocol_step[1:]))
                self._analyze_optional_step(protocol_part)
            elif _is_repeatable_step_spec(protocol_step):
                protocol_part = getattr(sys.modules[__name__], _get_array_name(protocol_step[1:]))
                self._analyze_repeatable_step(protocol_part)
            else:  # mandatory step spec, e.g. open-connection
                protocol_part = getattr(sys.modules[__name__], _get_array_name(protocol_step))
                self._analyze_protocol_part(protocol_part)

    def _analyze_optional_step(self, protocol_part):
        try:
            self._analyze_protocol_part(protocol_part)
        except ProtocolMismatch:
            pass  # protocol part can match 0 or 1 time

    def _analyze_repeatable_step(self, protocol_part):
        try:
            while True:
                self._analyze_protocol_part(protocol_part)
        except ProtocolMismatch:
            pass  # protocol part can match 0 or more times

    def _analyze_atomic_step(self, protocol_step, messages):
        try:
            message = messages.pop(0)
            if message_matches_step(protocol_step, message):
                self.processed_messages.append(message)
            else:
                messages.insert(0, message)
                raise ProtocolMismatch
        except IndexError:
            raise ProtocolMismatch()
