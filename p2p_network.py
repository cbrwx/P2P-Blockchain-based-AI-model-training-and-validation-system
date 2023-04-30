import socket
import threading
import json
import miner
from transaction import Transaction

class P2PNetwork:
    def __init__(self, blockchain, ip_address, port):
        self.blockchain = blockchain
        self.ip_address = ip_address
        self.port = port
        self.peers = []
        self.server = None
        self.start_server()

    def start_server(self):
        self.server = threading.Thread(target=self.run_server)
        self.server.start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip_address, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    data = conn.recv(1024)
                    if not data:
                        continue
                    request = json.loads(data.decode())
                    response = self.handle_request(request)
                    conn.sendall(json.dumps(response).encode())

    def handle_request(self, request):
        action = request.get("action")

        if action == "get_blocks":
            return self.blockchain.get_blocks()

        if action == "new_block":
            block_data = request.get("block")
            if self.blockchain.add_block_from_data(block_data):
                return {"status": "success"}
            else:
                return {"status": "failure"}

        if action == "get_peers":
            return self.peers

        if action == "new_peer":
            peer = request.get("peer")
            if peer not in self.peers:
                self.peers.append(peer)
            return {"status": "success"}

        if action == "find_transaction":
            tx_id = request.get("transaction_id")
            transaction = miner.find_transaction_by_id(self.blockchain, tx_id)
            if transaction:
                return {"status": "success", "transaction": transaction.to_dict()}
            else:
                return {"status": "not_found"}

        return {"status": "unknown_request"}

    def send_to_peers(self, request):
        for peer in self.peers:
            self.send_to_peer(peer, request)

    def send_to_peer(self, peer, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer["ip"], peer["port"]))
                s.sendall(json.dumps(request).encode())
                data = s.recv(1024)
                return json.loads(data.decode())
            except ConnectionRefusedError:
                print(f"Connection refused by {peer}")
                return {"status": "failure"}

    def broadcast_new_block(self, block):
        self.send_to_peers({"action": "new_block", "block": block.to_dict()})

    def add_peer(self, ip_address, port):
        self.peers.append({"ip": ip_address, "port": port})
        self.send_to_peer({"ip": ip_address, "port": port}, {"action": "new_peer", "peer": {"ip": self.ip_address, "port": self.port}})

    def find_transaction(self, transaction_id):
        response = self.send_to_peers({"action": "find_transaction", "transaction_id": transaction_id})
        if response["status"] == "success":
            return Transaction.from_dict(response["transaction"])
        else:
            return None
