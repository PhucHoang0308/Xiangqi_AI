import socket
import threading
import pickle

class XiangqiNetwork:
    def __init__(self, is_host, ip='127.0.0.1', port=5000):
        self.is_host = is_host
        self.ip = ip
        self.port = port
        self.conn = None
        self.addr = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def start(self):
        if self.is_host:
            self.sock.bind((self.ip, self.port))
            self.sock.listen(1)
            print(f"Waiting for connection on {self.ip}:{self.port}...")
            self.conn, self.addr = self.sock.accept()
            print(f"Connected by {self.addr}")
        else:
            self.sock.connect((self.ip, self.port))
            self.conn = self.sock
            print(f"Connected to host {self.ip}:{self.port}")
        self.running = True

    def send_move(self, from_pos, to_pos):
        data = pickle.dumps({'from': from_pos, 'to': to_pos})
        self.conn.sendall(data)

    def receive_move(self):
        data = b''
        while True:
            part = self.conn.recv(4096)
            if not part:
                break
            data += part
            try:
                move = pickle.loads(data)
                return move['from'], move['to']
            except Exception:
                continue
        return None, None

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()
        self.sock.close()
