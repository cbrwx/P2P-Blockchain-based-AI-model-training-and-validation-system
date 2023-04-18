import hashlib
import json
import time
from typing import List, Optional, Any
from model import SimpleLinearRegression

class Block:
    def __init__(self, index: int, timestamp: int, data: str, previous_hash: str, nonce: int, model_parameters: Any):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.model_parameters = model_parameters
        self.hash = self.compute_hash()

    def __repr__(self) -> str:
        return f'Block {self.index}: {self.hash}'

    def serialize(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True)

    @classmethod
    def deserialize(cls, block_data: str) -> 'Block':
        block_dict = json.loads(block_data)
        return cls(**block_dict)

    def compute_hash(self) -> str:
        block_string = self.serialize()
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty

    def create_genesis_block(self) -> Block:
        return Block(0, time.time(), "Genesis Block", "0", 0, None)

    def add_block(self, block: Block) -> None:
        if not self.is_valid_block(block, self.chain[-1]):
            raise ValueError("Invalid block")

        self.chain.append(block)

    def is_valid_block(self, new_block: Block, previous_block: Block) -> bool:
        if new_block.index != previous_block.index + 1:
            return False
        if new_block.previous_hash != previous_block.hash:
            return False
        if new_block.compute_hash() != new_block.hash:
            return False
        if not new_block.hash.startswith("0" * self.difficulty):
            return False
        return True

    def create_new_block(self, data: str, previous_hash: str, nonce: int, model_parameters: Any) -> Block:
        new_block = Block(len(self.chain), time.time(), data, previous_hash, nonce, model_parameters)
        return new_block

    def mine_block(self, data: str, model: SimpleLinearRegression, X: List[float], y: List[float]) -> Block:
        previous_block = self.chain[-1]
        new_block = self.create_new_block(data, previous_block.hash, 0, model.serialize())
        while not new_block.hash.startswith("0" * self.difficulty):
            model.train(X, y, epochs=1)
            new_block.model_parameters = model.serialize()
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()
        return new_block

    def serialize(self) -> str:
        return json.dumps([block.serialize() for block in self.chain], sort_keys=True)

    @classmethod
    def deserialize(cls, chain_data: str) -> 'Blockchain':
        chain_list = json.loads(chain_data)
        blockchain = cls()
        blockchain.chain = [Block.deserialize(block_data) for block_data in chain_list]
        return blockchain

if __name__ == "__main__":
    # Example usage of the Blockchain class
    blockchain = Blockchain()
    model = SimpleLinearRegression()

    # Replace X and y with actual training data
    X = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    block1 = blockchain.mine_block("Training Data 1", model, X, y)
    blockchain.add_block(block1)

    block2 = blockchain.mine_block("Training Data 2", model, X, y)
    blockchain.add_block(block2)

    print(blockchain.chain)

    serialized_blockchain = blockchain.serialize()
    print(serialized_blockchain)

    deserialized_blockchain = Blockchain.deserialize(serialized_blockchain)
    print(deserialized_blockchain.chain)
