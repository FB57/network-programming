import argparse, socket

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more: 
            raise EOFError('was expecting %d bytes but only received '
                            ' %d bytes before the socket closed'
                            % (length, len(data)))
        data += more
    return data

def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((interface, port))
    sock.listen(1)
    print('Listening at ', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        print('we have received the connection from ', sockname)
        print('Sock name: ', sc.getsockname())
        print('Socket peer: ', sc.getpeername())
        message = recvall(sc, 16)
        print('Message is Received')
        sc.sendall(b'thank you client')
        sc.close()
        print('Reply is sent to the client')

def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print('client has been assigned socket name', sock.getsockname())
    sock.sendall(b'Hi Server, we are learning NP TCP program')
    reply = recvall(sock, 16)
    print('The server said', repr(reply))
    sock.close()

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description = 'Send and receive over TCP')
    parser.add_argument('role', choices = choices, help = 'which role to play')
    parser.add_argument('host', help = 'interface the server listens at; '
                        ' host the client sends to')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)