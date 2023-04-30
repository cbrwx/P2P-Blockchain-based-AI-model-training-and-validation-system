import sys
import threading
from miner import Miner
from p2p_network import P2PNode
from blockchain import Blockchain
from consensus import Consensus
from your_ai_module import YourAIModel
from masternode import Masternode

def main():
    if len(sys.argv) != 3:
        print("Usage: main.py [node_port] [masternode_flag]")
        sys.exit(1)

    node_port = int(sys.argv[1])
    is_masternode = sys.argv[2].lower() == "true"

    # Initialize the blockchain and consensus algorithm
    blockchain = Blockchain()
    consensus = Consensus(blockchain)

    # Initialize and load the AI model
    ai_model = YourAIModel()
    ai_model.load()

    # Initialize the P2P network
    p2p_node = P2PNode(port=node_port)
    p2p_node.start()

    if is_masternode:
        # Initialize and run the masternode
        masternode = Masternode(ai_model, p2p_node)
        masternode_thread = threading.Thread(target=masternode.run)
        masternode_thread.start()

        # Wait for the masternode thread to finish (which it won't in normal operation)
        masternode_thread.join()
    else:
        # Initialize and run the miner
        miner = Miner(p2p_node, blockchain, ai_model)
        miner_thread = threading.Thread(target=miner.run)
        miner_thread.start()

        # Wait for the miner thread to finish (which it won't in normal operation)
        miner_thread.join()

if __name__ == "__main__":
    main()

    print("python main.py [node_port] [masternode_flag]")
