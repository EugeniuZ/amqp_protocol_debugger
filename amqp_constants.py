ACCESS_REFUSED = 403
CHANNEL_ERROR = 504
COMMAND_INVALID = 503
CONNECTION_FORCED = 320
CONTENT_TOO_LARGE = 311
FRAME_BODY = 3
FRAME_END = 206
FRAME_ERROR = 501
FRAME_HEADER = 2
FRAME_HEARTBEAT = 8
FRAME_METHOD = 1
FRAME_MIN_SIZE = 4096
INTERNAL_ERROR = 541
INVALID_PATH = 402
NOT_ALLOWED = 530
NOT_FOUND = 404
NOT_IMPLEMENTED = 540
NO_CONSUMERS = 313
PRECONDITION_FAILED = 406
REPLY_SUCCESS = 200
RESOURCE_ERROR = 506
RESOURCE_LOCKED = 405
SYNTAX_ERROR = 502
UNEXPECTED_FRAME = 505

AMQP_METHODS = {
10: 
{
10: "connection.start",
11: "connection.start-ok",
20: "connection.secure",
21: "connection.secure-ok",
30: "connection.tune",
31: "connection.tune-ok",
40: "connection.open",
41: "connection.open-ok",
50: "connection.close",
51: "connection.close-ok",
},
20: 
{
10: "channel.open",
11: "channel.open-ok",
20: "channel.flow",
21: "channel.flow-ok",
40: "channel.close",
41: "channel.close-ok",
},
40: 
{
10: "exchange.declare",
11: "exchange.declare-ok",
20: "exchange.delete",
21: "exchange.delete-ok",
30: "exchange.bind",
31: "exchange.bind-ok",
40: "exchange.unbind",
51: "exchange.unbind-ok",
},
50: 
{
10: "queue.declare",
11: "queue.declare-ok",
20: "queue.bind",
21: "queue.bind-ok",
50: "queue.unbind",
51: "queue.unbind-ok",
30: "queue.purge",
31: "queue.purge-ok",
40: "queue.delete",
41: "queue.delete-ok",
},
60: 
{
10: "basic.qos",
11: "basic.qos-ok",
20: "basic.consume",
21: "basic.consume-ok",
30: "basic.cancel",
31: "basic.cancel-ok",
40: "basic.publish",
50: "basic.return",
60: "basic.deliver",
70: "basic.get",
71: "basic.get-ok",
72: "basic.get-empty",
80: "basic.ack",
90: "basic.reject",
100: "basic.recover-async",
110: "basic.recover",
111: "basic.recover-ok",
120: "basic.nack",
},
90: 
{
10: "tx.select",
11: "tx.select-ok",
20: "tx.commit",
21: "tx.commit-ok",
30: "tx.rollback",
31: "tx.rollback-ok",
},
85: 
{
10: "confirm.select",
11: "confirm.select-ok",
},
}
