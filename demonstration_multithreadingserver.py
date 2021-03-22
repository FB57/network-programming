import argparse, socket, time
from threading import Thread

tasks = {b'Beautiful is better than?' : b'Ugly.',
            b'Explicit is better than?' : b'Implicit.',
            b'Which is this Network Programming Sessions?' : b'2020-2021.'}

def create_srv_socket(address) :
    """Build and return a listening server socket."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener

def accept_connections_forever(listener) :
    """Forever answer incoming connections on a listening socket."""
    while True :
        sock, address = listener.accept()
        print('Accepted connnection from {}'.format(address))
        handle_conversation(sock, address)

def handle_conversation(sock, address) :
    """Converse with a client over 'sock' until they are done talking."""
    try :
        while True :
            handle_request(sock)
    
    except EOFError :
        print('Client socket to {} has closed'.format(address))
    except Exception as e :
        print('Client {} error : {}'.format(address, e))
    finally :
        sock.close()

def handle_request(sock) :
    """Receive a single client request on 'sock' and send the answer."""
    task = recv_until(sock, b'?')
    answer = get_answer(task)
    sock.sendall(answer)

def recv_until(sock, suffix) :
    """Receive bytes over socket 'sock' until we receive the 'suffix'."""
    message = sock.recv(4096)
    if not message :
        raise EOFError('socket closed')
    while not messsage.endswith(suffix) :
        data = sock.recv(4096)
        if not data :
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message

def get_answer(task) :
    time.sleep(2)       # increase to simulate an expensive operation
    return tasks.get(task, b'Error : unknown task')

def parse_command_line(description) :
    """Parse command line and return a socket address."""
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument('host', help = 'IP or hostname')
    parser.add_argument('-p', metavar = 'port', type = int, default = 1060, help = 'TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)
    return address

def start_threads(listener, workers = 4):
    t = (listener, )
    for i in range(workers) :
        Thread(target = accept_connections_forever, args = t).start()

if __name__ == '__main__':
    address = parse_command_line('multi-threaded server')
    listener = create_srv_socket(address)
    start_threads(listener)