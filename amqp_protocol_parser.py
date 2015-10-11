from amqp_constants import *
from amqp_data_types import *
from amqp_messages import AMQPFrame, AMQPProtocolHeader

KNOWN_FRAME_TYPES = [FRAME_METHOD, FRAME_HEADER, FRAME_BODY, FRAME_HEARTBEAT]

FRAME_END_MARKER = ord(b'\xCE')

CLIENT = "CLIENT"
SERVER = "SERVER"


class MalformedMessage(Exception):
    pass


class AMQPStreamParser(object):
    def __init__(self, bytes, source):
        self.bytes = bytes
        self.source = source
        if source == 'CLIENT':
            self.parse_frame = self.parse_frame_init
        else:
            self.parse_frame = self.parse_standard_frame

    def __iter__(self):
        return self

    def __next__(self):
        return self.next_message()

    def next_message(self):
        if not self.bytes:
            raise StopIteration
        return self.parse_frame()

    def parse_frame_init(self):
        self.parse_frame = self.parse_standard_frame
        if self._is_protocol_header():
            return self._extract_protocol_header()
        else:
            return self.parse_frame()

    def parse_standard_frame(self):
        frame_type, self.bytes = extract_octet(self.bytes)
        if frame_type not in KNOWN_FRAME_TYPES:
            raise MalformedMessage("Unknown frame type: %d" % frame_type)
        channel_id, self.bytes = extract_short_uint(self.bytes)
        payload_size, self.bytes = extract_long_uint(self.bytes)
        if len(self.bytes) < payload_size + 1:
            raise MalformedMessage("Truncated frame")
        payload, self.bytes = self.bytes[:payload_size], self.bytes[payload_size:]
        frame_end, self.bytes = extract_octet(self.bytes)
        if frame_end != FRAME_END_MARKER:
            raise MalformedMessage("Invalid frame end marker: %s" % hex(frame_end))
        return AMQPFrame(self.source, frame_type, channel_id, payload)

    def _is_protocol_header(self):
        return self.bytes[:4] == b'AMQP'

    def _extract_protocol_header(self):
        amqp_literal, self.bytes = self.bytes[:4], self.bytes[4:]
        protocol_id, self.bytes = extract_octet(self.bytes)
        protocol_version_major, self.bytes = extract_octet(self.bytes)
        protocol_version_minor, self.bytes = extract_octet(self.bytes)
        protocol_version_revision, self.bytes = extract_octet(self.bytes)
        return AMQPProtocolHeader(protocol_id, protocol_version_major, protocol_version_minor, protocol_version_revision)
