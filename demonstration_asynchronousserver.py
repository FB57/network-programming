import select, argparse, socket, time

tasks = {b'Beautiful is better than?' : b'Ugly',
            b'Explicit is better than?' : b'Implicit',
            b'Which is this Network Programming Session?' : b'2020-2021'}

def all_events_forever(poll_object) :
    while True :
        for fd, event in poll_object.poll() :
            yield fd, event

def serve(listener) :
    sockets = {listener.fileno(): listener}
    addresses = {}
    bytes_received = {}
    bytes_to_send = {}
    poll_object = select.poll()
    poll_object.register(listener, select.POLLIN)
    for fd, event in all_events_forever(poll_object) :
        sock = sockets[fd]

        # Server is receiving a new connection
        if sock is listener :
            sock, address = sock.accept()
            print('Accepted connection from {}'.format(address))
            sock.setblocking(True)
            sockets[sock.fileno()] = sock
            addresses[sock] = address
            poll_object.register(sock, select.POLLIN)
        
        # Socket is closed
        elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL) :
            address = addresses.pop(sock)
            rb = bytes_received.pop(sock, 'b')
            sb = bytes_to_send.pop(sock, 'b')
            if rb :
                print('abnormal close, client {} sent {} but then closed'.format(address, rb))
            elif sb :
                print('abnormal close, client {} closed before we sent'.format(address, sb))
            else :
                print('Normal closing by client {}'.format(address))
            poll_object.unregister(fd)
            del sockets[fd]

        elif event & select.POLLIN :
            more_data = sock.recv(4096)
            if not more_data :
                sock.close()
                continue
            data = bytes_received.pop(sock, 'b')
            if data.endswith(b'?') :
                bytes_to_send[sock] = get_answer(data)
                poll_object.modify(sock, select.POLLOUT)
            else :
                bytes_received[sock] = data

        # Server is ready to send to client
        elif event & select.POLLOUT :
            data = bytes_to_send.pop(sock)
            n = sock.send(data)
            if n < len(data) :
                bytes_to_send[sock] = data[n:]
            else :
                poll_object.modify(sock, select.POLLIN)

def get_answer(task) :
    time.sleep(2)       # increase to simulate an expensive operation
    return tasks.get(task, b'Error: unknown task')

def create_srv_socket(address) :
    """Build and return a listening server socket."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener

def parse_command_line(description) :
    """Parse command line and return a socket address."""
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument('host', help = 'IP or hostname')
    parser.add_argument('-p', metavar = 'port', type = int, default = 1060, help = 'TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)
    return address

if __name__ == '__main__' :
    address = parse_command_line('low-level async server')
    listener = create_srv_socket(address)
    serve(listener)