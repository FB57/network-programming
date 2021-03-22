import argparse, random, socket, time
from datetime import datetime

tasks = {b'Beautiful is better than?': b'Ugly.',
            b'Explicit is better than?': b'Implicit.',
            b'Which is this Network Programming Session?': b'2020-2021.'}

def client(address, cause_error = False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    for task in random.sample(list(tasks), 3):
        sock.sendall(task)
        print(recv_until(sock, b'.'))
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time = ", current_time)
    sock.close()

def recv_until(sock, suffix):
    """Receive bytes over socket 'sock' until we receive the 'suffix'."""
    message = sock.recv(4096)
    if not message:
        raise EOFError('socket closed')
    while not message.endswith(suffix):
        data = sock.recv(4096)
        if not data:
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Example client')
    parser.add_argument('host', help = 'IP or hostname')
    parser.add_argument('-e', action = 'store_true', help = 'cause an error')
    parser.add_argument('-p', metavar = 'port', type = int, default = 1060, help = 'TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)
    client(address, args.e)