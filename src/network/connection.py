import socket
import threading
import queue
import json
from contextlib import closing

DEFAULT_PORT = 5555


def get_local_ip() -> str:
    """Best-effort to get local LAN IP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())


class NetworkConnection:
    """
    Lightweight line-delimited JSON messaging over TCP.
    One side acts as host (server), the other as client.
    """
    def __init__(self):
        self.role = None  # 'host' or 'client'
        self.port = DEFAULT_PORT
        self.server_sock = None
        self.sock = None
        self.recv_thread = None
        self.accept_thread = None
        self.queue = queue.Queue()
        self.connected = threading.Event()
        self.stop_event = threading.Event()
        self.bound_ip = None

    # ---------- Hosting ----------
    def start_host(self, port: int = DEFAULT_PORT) -> str:
        self.role = 'host'
        self.port = port
        self.bound_ip = get_local_ip()
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', self.port))
        self.server_sock.listen(1)

        def accept_loop():
            try:
                self.server_sock.settimeout(0.5)
                while not self.stop_event.is_set():
                    try:
                        conn, addr = self.server_sock.accept()
                        self.sock = conn
                        self.connected.set()
                        self._start_recv_thread()
                        break
                    except socket.timeout:
                        continue
            except Exception as e:
                self.queue.put({'type': 'error', 'message': str(e)})

        self.accept_thread = threading.Thread(target=accept_loop, daemon=True)
        self.accept_thread.start()
        return self.bound_ip

    # ---------- Joining ----------
    def connect(self, host: str, port: int = DEFAULT_PORT) -> bool:
        self.role = 'client'
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            self.connected.set()
            self._start_recv_thread()
            return True
        except Exception as e:
            self.queue.put({'type': 'error', 'message': str(e)})
            return False

    # ---------- Messaging ----------
    def _start_recv_thread(self):
        def recv_loop():
            buf = b''
            try:
                self.sock.settimeout(0.5)
                while not self.stop_event.is_set():
                    try:
                        data = self.sock.recv(4096)
                        if not data:
                            self.queue.put({'type': 'disconnect'})
                            break
                        buf += data
                        while b'\n' in buf:
                            line, buf = buf.split(b'\n', 1)
                            if not line:
                                continue
                            try:
                                msg = json.loads(line.decode('utf-8'))
                                self.queue.put(msg)
                            except json.JSONDecodeError:
                                continue
                    except socket.timeout:
                        continue
            except Exception as e:
                self.queue.put({'type': 'error', 'message': str(e)})
        self.recv_thread = threading.Thread(target=recv_loop, daemon=True)
        self.recv_thread.start()

    def send(self, obj: dict) -> bool:
        if not self.connected.is_set() or not self.sock:
            return False
        try:
            payload = (json.dumps(obj) + '\n').encode('utf-8')
            self.sock.sendall(payload)
            return True
        except Exception as e:
            self.queue.put({'type': 'error', 'message': str(e)})
            return False

    def get_message(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None

    def close(self):
        self.stop_event.set()
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        try:
            if self.server_sock:
                self.server_sock.close()
        except Exception:
            pass
        self.sock = None
        self.server_sock = None
        self.connected.clear()
