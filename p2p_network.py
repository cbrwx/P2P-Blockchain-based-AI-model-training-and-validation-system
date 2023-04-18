import threading
import socket
import json
import random
from typing import Any, Callable, List

class P2PNode:
    def __init__(self, host: str = "0.0.0.0", port: int = 5000, peers: List[str] = None):
        self.host = host
        self.port = port
        self.peers = peers if peers else []
        self.connections = []
        self.message_handlers = []

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        threading.Thread(target=self._listen_for_connections).start()
        threading.Thread(target=self._connect_to_peers).start()

    def _listen_for_connections(self) -> None:
        while True:
            conn, _ = self.server_socket.accept()
            self.connections.append(conn)
            threading.Thread(target=self._handle_connection, args=(conn,)).start()

    def _connect_to_peers(self) -> None:
        for peer in self.peers:
            try:
                host, port = peer.split(":")
                conn = socket.create_connection((host, int(port)))
                self.connections.append(conn)
                threading.Thread(target=self._handle_connection, args=(conn,)).start()
            except Exception as e:
                print(f"Failed to connect to peer {peer}: {e}")

    def _handle_connection(self, conn: socket.socket) -> None:
        while True:
            try:
                message = conn.recv(1024).decode("utf-8")
                if not message:
                    break

                message = json.loads(message)
                for handler in self.message_handlers:
                    handler(message)
            except Exception as e:
                print(f"Failed to handle message: {e}")
                break

        conn.close()
        self.connections.remove(conn)

    def add_message_handler(self, handler: Callable[[Any], None]) -> None:
        self.message_handlers.append(handler)

    def broadcast(self, message: Any) -> None:
        message_str = json.dumps(message)
        for conn in self.connections:
            try:
                conn.sendall(message_str.encode("utf-8"))
            except Exception as e:
                print(f"Failed to send message: {e}")

if __name__ == "__main__":
    p2p_node = P2PNode(port=random.randint(5000, 6000))
    p2p_node.start()
    print(f"Node started at {p2p_node.host}:{p2p_node.port}")
