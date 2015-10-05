"""
The script receives the dump of bytes exchanged on 2 socket connections between 2 AMQP participants and prints a nice
 representation of the messages and the order in which they could have been exchanged.

 To get the dump you could:
 1. create a folder and cd into it
 2. execute `sudo tcpflow -i any -a  port 5672`
 3. select the 2 files that correspond to a client-server exchange
    * to find out a specific client connection you need to know the port. To get the port execute `lsof -nP -p <PID> | grep TCP`
    where <PID> is the pid of the client process.
"""

import sys

from amqp_protocol_parser import AMQPStreamParser
from amqp_protocol import ProtocolDetective


def main():
    """
    Usage: client_message_dump_file server_message_dump_file [output_file]
    """
    client_message_dump_file = sys.argv[1]
    server_message_dump_file = sys.argv[2]

    if len(sys.argv) == 4:
        output_stream = open(sys.argv[3])
    else:
        output_stream = sys.stdout

    try:
        client_stream_parser = AMQPStreamParser(_get_protocol_bytes(client_message_dump_file), "CLIENT")
        server_stream_parser = AMQPStreamParser(_get_protocol_bytes(server_message_dump_file), "SERVER")

        client_messages = [message for message in client_stream_parser]
        server_messages = [message for message in server_stream_parser]

        messages = ProtocolDetective(client_messages, server_messages).analyze()

        for message in messages:
            print(message, file=output_stream, flush=True)
    finally:
        if output_stream != sys.stdout:
            output_stream.close()


def _get_protocol_bytes(filename):
    with open(filename, 'r+b') as f:
        return f.read()

if __name__ == "__main__":
    main()
