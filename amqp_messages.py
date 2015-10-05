from amqp_constants import *
from amqp_data_types import *

FRAME_TYPES = {
    0: "PROTOCOL_HEADER",
    FRAME_METHOD: "METHOD",
    FRAME_HEADER: "HEADER",
    FRAME_BODY: "BODY",
    FRAME_HEARTBEAT: "HEARTBEAT"
}


def parse_payload(amqp_frame):
    payload_string = None
    payload = amqp_frame.payload
    if amqp_frame.type == FRAME_METHOD:
        amqp_frame.class_id, payload = extract_short_uint(payload)
        amqp_frame.method_id, payload = extract_short_uint(payload)
        amqp_frame.args = payload
        payload_string = "%s(%s)" % (AMQP_METHODS[amqp_frame.class_id][amqp_frame.method_id], payload)
    if amqp_frame.type == FRAME_HEADER:
        amqp_frame.class_id, payload = extract_short_uint(payload)
        amqp_frame.weight, payload = extract_short_uint(payload)
        amqp_frame.frame_body_size, payload = extract_long_uint(payload)
        amqp_frame.property_flags = payload
        payload_string = "%s.HEADER(weight=%d, frame_body_size=%d, property_flags=%s)" % (
            list(AMQP_METHODS[amqp_frame.class_id].values())[0].split(".")[0],
            amqp_frame.weight,
            amqp_frame.frame_body_size,
            repr(payload)
        )
    if amqp_frame.type == FRAME_BODY:
        payload_string = payload
    return payload_string


class AMQPFrame(object):
    def __init__(self, source, frame_type, channel_id, payload):
        self._source = source  # client or server
        self.type = frame_type
        self.frame_type_string = FRAME_TYPES[frame_type]
        self.channel = channel_id
        self.payload_len = len(payload)
        self.payload = payload
        self.parsed_payload = parse_payload(self)
        self._out_of_order = False

    @property
    def out_of_order(self):
        return self._out_of_order

    @out_of_order.setter
    def out_of_order(self, value):
        self._out_of_order = value


    @property
    def source(self):
        return self._source


    @property
    def method(self):
        if self.type == FRAME_METHOD:
            return AMQP_METHODS[self.class_id][self.method_id]
        elif self.type == FRAME_HEADER:
            return "%s.HEADER" % self.class_id
        elif self.type == FRAME_BODY:
            return "BODY"

    def __eq__(self, other):
        try:
            assert isinstance(other, AMQPFrame)
            assert self._source == other._source
            assert self.type == other.type
            assert self.channel == other.channel
            assert self.payload == other.payload
            return True
        except AssertionError:
            return False

    def __repr__(self):
        return "AMQPFrame(%s, %s, %d, %s)" % (self._source,
                                              self.type,
                                              self.channel,
                                              self.payload)

    def __str__(self):
        out_of_order_marker = "(!) " if self._out_of_order else ""
        return '%s%s: |%s|%d|%d|%s|%s|' % (out_of_order_marker,
                                           self._source,
                                           self.frame_type_string,
                                           self.channel,
                                           self.payload_len,
                                           self.parsed_payload,
                                           'END')


class AMQPProtocolHeader(object):
    def __init__(self, proto_id, proto_version_major, proto_version_minor, proto_version_revision):
        self.proto_id = proto_id
        self.major = proto_version_major
        self.minor = proto_version_minor
        self.rev = proto_version_revision

    @property
    def source(self):
        return "CLIENT"

    @property
    def method(self):
        return "protocol-header"

    def __eq__(self, other):
        try:
            assert isinstance(other, AMQPProtocolHeader)
            assert self.proto_id == other.proto_id
            assert self.major == other.major
            assert self.minor == other.minor
            assert self.rev == other.rev
            return True
        except AssertionError:
            return False

    def __repr__(self):
        return 'AMQPProtocolHeader(%s, %s, %s, %s)' % (self.proto_id,
                                                       self.major,
                                                       self.minor,
                                                       self.rev)

    def __str__(self):
        return 'CLIENT: |PROTOCOL_HEADER| AMQP %d %d.%d.%d |' % (self.proto_id,
                                                                 self.major,
                                                                 self.minor,
                                                                 self.rev)
