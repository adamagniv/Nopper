import socket

SERV_IP_ADDR = "20.0.0.10"
#SERV_IP_ADDR = "127.0.0.1"
PORT = 9002
MSG_LEN = 512

class NopConn:
    def __init__(self, init_server=False):
        self.is_server = init_server
        self.sock = ''
        self.serv_sock = ''

    def __del__(self):
        self.teardown()

    def setup(self):
        if (self.is_server):
            # setting up the server for connections on the master
            self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serv_sock.bind((SERV_IP_ADDR, PORT))
            self.serv_sock.listen(1)
            # accept connection from remote client
            self.sock, _ = self.serv_sock.accept()
        else:
            # connect to remote server
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERV_IP_ADDR, PORT))

    def teardown(self):
        self.sock.close()
        if (self.is_server):
             self.serv_sock.close()

    def NopSend(self, msg):
        try:
            self.sock.send(msg.encode())
        except:
            self.sock.close()

    def NopRecv(self):
        try:
            msg = self.sock.recv(MSG_LEN).decode()
        except:
            self.sock.close()
        return msg