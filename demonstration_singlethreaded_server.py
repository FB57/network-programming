import argparse, socket, time

tasks = {b'Beautiful is better than?': b'Ugly.',
            b'Explicit is better than?': b'Implicit.',
            b'Which is this Network Programming Session?': b'2020-2021.'}

def create_srv_socket(address):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener

def accept_connection_forever(listener):
    while True:
        sock, address = listener.accept()
        print('Accepted connection from {}'.format(address))
        handle_conversation(sock, address)

def handle_conversation(sock, address):
    try:
        while True:
            handle_request(sock)
    except EOFError:
        print('Client socket to {} has closed'.format(address))
    except Exception as e:
        print('Client {} error: {}'.format(address, e))
    finally:
        sock.close()

def handle_request(sock):
    task = recv_until(sock, b'?')
    answer = get_answer(task)
    sock.sendall(answer)

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

def get_answer(task):
    time.sleep(2)
    return tasks.get(task, b'Task not in db')

def parse_command_line(description):
    """Parse command line and return a socket address."""
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument('host', help = 'IP or hostname')
    parser.add_argument('-p', metavar = 'port', type = int, default = 1060, help = 'TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)
    return address

if __name__ == '__main__':
    address = parse_command_line('simple single-threaded server')
    listener = create_srv_socket(address)
    accept_connection_forever(listener)