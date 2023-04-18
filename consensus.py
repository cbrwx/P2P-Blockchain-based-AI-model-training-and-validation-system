import json
from typing import Dict, Optional
from blockchain import compute_hash

class Consensus:
    def __init__(self, blockchain: Any):
        self.blockchain = blockchain

    def validate_block(self, block: Dict) -> bool:
        serialized_block = json.dumps(block, sort_keys=True)

        # Ensure the block's hash is valid
        if compute_hash(block) != block["hash"]:
            return False

        return True

    def validate_chain(self) -> bool:
        for i in range(1, len(self.blockchain.chain)):
            prev_block = self.blockchain.chain[i - 1]
            curr_block = self.blockchain.chain[i]

            if not self.validate_block(curr_block):
                return False

            if curr_block["previous_hash"] != self.blockchain.hash(prev_block):
                return False

        return True
