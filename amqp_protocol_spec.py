PROTOCOL = [
    "open-connection",
    "?use-connection",  # changed the spec from * to ? (i.e parallel usages of the channel are disallowed)
    "close-connection"
]

OPEN_CONNECTION = [
    "C:protocol-header",
    "S:connection.start",
    "C:connection.start-ok",
    "*challenge",
    "S:connection.tune",
    "C:connection.tune-ok",
    "C:connection.open",
    "S:connection.open-ok"
]

CHALLENGE = [
    "S:connection.secure",
    "C:connection.secure-ok",
]

USE_CONNECTION = [
    "*channel"
]

CHANNEL = [
    "open-channel",
     "?use-channel",
    "close-channel"
]


OPEN_CHANNEL = [
    "C:channel.open",
    "S:channel.open-ok",
]

USE_CHANNEL = [
    "use-channel-client-init | use-channel-server-init | *functional-class"
]

USE_CHANNEL_CLIENT_INIT = [
    "C:channel.flow",
    "S:channel.flow-ok"
]

USE_CHANNEL_SERVER_INIT = [
    "S:channel.flow",
    "C:channel.flow-ok"
]


FUNCTIONAL_CLASS = [
    "*exchange | *queue | *basic | *tx | *confirm"  # TODO: generalize to * and then fix ?use-connection
]


EXCHANGE = [
    "exchange-declare | exchange-delete"
]

EXCHANGE_DECLARE = [
    "C:exchange.declare",
    "S:exchange.declare-ok"
]

EXCHANGE_DELETE = [
    "C:exchange.delete",
    "S:exchange.delete-ok"
]


QUEUE = [
    "queue-declare | queue-bind | queue-unbind | queue_purge | queue_delete"
]


QUEUE_DECLARE = [
    "C:queue.declare",
    "S:queue.declare.ok"
]

QUEUE_BIND = [
    "C:queue.bind",
    "S:queue.bind-ok"
]

QUEUE_UNBIND = [
    "C:queue.unbind",
    "S:queue.unbind-ok"
]

QUEUE_PURGE = [
    "C:queue.purge",
    "S:queue.purge-ok"
]

QUEUE_DELETE = [
    "C:queue.delete",
    "S:queue.delete-ok"
]


BASIC = [
    "qos | consume | cancel | publish | return-failed | deliver | get | ack | recover-async | recover"
]

QOS = [
    "C:basic.qos",
    "S:basic.qos-ok"
]

CONSUME = [
    "C:basic.consume",
    "S:basic.consume-ok"
]

CANCEL = [
    "C:basic.cancel",
    "S:basic.cancel-ok"
]

PUBLISH = [
    "C:basic.publish",
    "C:BODY"
]

RETURN_FAILED = [
    "S:basic.return",
    "S:BODY"
]


DELIVER = [
    "S:basic.deliver",
    "S:BODY"
]


GET = [
    "get-content | get-empty"
]

GET_CONTENT = [
    "C:basic.get",
    "S:basic.get-ok",
    "S:BODY"
]

GET_EMPTY = [
    "C:basic.get",
    "S:basic.get-empty"
]

ACK = [
    "C:basic.ack"
]

REJECT = [
    "C:basic.reject"
]

RECOVER_ASYNC = [
    "C:basic.recover-async"
]

RECOVER = [
    "C:basic.recover",
    "S:basic.recover-ok"
]

TX = [
    "tx-select | tx-commit | tx-rollback"
]

TX_SELECT = [
    "C:tx.select",
    "S:tx.select-ok"
]

TX_COMMIT = [
    "C:tx.commit",
    "S:tx.commit-ok"
]

TX_ROLLBACK = [
    "C:tx.rollback",
    "S:tx.rollback-ok"
]

CONFIRM = [
    "C:confirm.select",
    "S:confirm.select-ok"
]


CLOSE_CHANNEL = [
    "channel-close-client-init | channel-close-server-init"
]


CHANNEL_CLOSE_CLIENT_INIT = [
    "C:channel.close",
    "S:channel.close-ok"
]

CHANNEL_CLOSE_SERVER_INIT = [
    "S:channel.close"
    "C:channel.close-ok"
]

CLOSE_CONNECTION = [
    "client-close | server-close"
]

CLIENT_CLOSE = [
    "C:connection.close",
    "S:connection.close"
]

SERVER_CLOSE = [
    "S:connection.close",
    "C:connection.close"
]
