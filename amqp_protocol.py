import sys

from itertools import zip_longest

from amqp_protocol_spec import *
from amqp_constants import FRAME_HEARTBEAT


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


def _is_mandatory_step(step):
    return not (step.startswith("S:") or step.startswith("C:"))


def message_matches_step(step, message):
    return message.source.startswith(step[0]) and message.method == step[2:]


def get_protocol_part(protocol_part_name):
    return getattr(sys.modules[__name__], _get_array_name(protocol_part_name))


class ProtocolMismatch(Exception):
    pass


class ProtocolDetective(object):
    def __init__(self, client_messages, server_messages):
        self.processed_messages = []
        self.client_messages = client_messages
        self.server_messages = server_messages

    def analyze(self):
        try:
            self._analyze_protocol_part("protocol")
        except ProtocolMismatch as e:
            print(e, file=sys.stderr, flush=True)
            for client_message, server_message in zip_longest(self.client_messages, self.server_messages):
                if client_message:
                    client_message.out_of_order = True
                    self.processed_messages.append(client_message)
                if server_message:
                    server_message.out_of_order = True
                    self.processed_messages.append(server_message)
        return self.processed_messages

    def _analyze_protocol_part(self, step):
        protocol_table = get_protocol_part(step)
        for current_step in protocol_table:
            if _is_alternative_step_spec(current_step):
                protocol_alternatives = current_step.split(" | ")
                for protocol_alternative in protocol_alternatives:
                    if _is_client_step(protocol_alternative):
                        self._analyze_atomic_step(protocol_alternative, self.client_messages)
                        break
                    elif _is_server_step(protocol_alternative):
                        self._analyze_atomic_step(protocol_alternative, self.server_messages)
                        break
                    elif _is_repeatable_step_spec(protocol_alternative) or \
                            _is_optional_step_spec(protocol_alternative):
                        raise Exception("Can't have quantifiers applied to an alternative rule. "
                                        "Use them only in step sequences.")
                    else:  # non-atomic mandatory alternative
                        try:
                            self._analyze_protocol_part(protocol_alternative)
                            break
                        except ProtocolMismatch:
                            pass  # the alternative did not match try the next one
                else:  # none of the alternatives matched
                    raise ProtocolMismatch("None of the protocol alternatives matched:\n"
                                           "alternatives:%s\n"
                                           "current message: %s" % (protocol_alternatives, current_step))
            elif _is_optional_step_spec(current_step):
                self._analyze_optional_step(current_step[1:])
            elif _is_repeatable_step_spec(current_step):
                self._analyze_repeatable_step(current_step[1:])
            elif _is_mandatory_step(current_step):
                self._analyze_protocol_part(current_step)
            elif _is_client_step(current_step):
                self._analyze_atomic_step(current_step, self.client_messages)
            elif _is_server_step(current_step):
                self._analyze_atomic_step(current_step, self.server_messages)
            else:
                raise ProtocolMismatch("Invalid protocol step spec: %s" % current_step)

    def _analyze_optional_step(self, current_step):
        try:
            if _is_client_step(current_step):
                self._analyze_atomic_step(current_step, self.client_messages)
            elif _is_server_step(current_step):
                self._analyze_atomic_step(current_step, self.server_messages)
            else:
                self._analyze_protocol_part(current_step)
        except ProtocolMismatch:
            pass  # protocol part can match 0 or 1 time

    def _analyze_repeatable_step(self, current_step):
        try:
            while True:
                if _is_client_step(current_step):
                    self._analyze_atomic_step(current_step, self.client_messages)
                elif _is_server_step(current_step):
                    self._analyze_atomic_step(current_step, self.server_messages)
                else:
                    self._analyze_protocol_part(current_step)
        except ProtocolMismatch:
            pass  # protocol part can match 0 or more times

    def _analyze_atomic_step(self, current_step, messages):
        try:
            message = messages.pop(0)
            while message.type == FRAME_HEARTBEAT:
                self.processed_messages.append(message)
                message = messages.pop(0)
            if message_matches_step(current_step, message):
                self.processed_messages.append(message)
            else:
                messages.insert(0, message)
                raise ProtocolMismatch("Atomic step did not match:\n"
                                       "actual: %s\n"
                                       "expected: %s" % (message, current_step))
        except IndexError:
            raise ProtocolMismatch("Message stream empty but protocol is ongoing at: %s" % current_step)
