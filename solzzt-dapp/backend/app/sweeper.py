from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import Message
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
from solana.rpc.async_api import AsyncClient
from spl.token.instructions import close_account, CloseAccountParams
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.keypair import Keypair 
import base64

class Sweeper:
    def __init__(self, rpc_client: AsyncClient):
        self.client = rpc_client

    def create_close_instructions(self, zombie_addresses: list[str], owner: Pubkey) -> list[Instruction]:
        instructions = []
        for addr in zombie_addresses:
            # Create standard SPL Token Close instruction
            ix = close_account(CloseAccountParams(
                account=Pubkey.from_string(addr),
                dest=owner,
                owner=owner,
                program_id=TOKEN_PROGRAM_ID,
                signers=[owner]
            ))
            instructions.append(ix)
        return instructions

    async def get_optimal_priority_fee(self) -> int:
        """
        Fetches recent prioritization fees from the RPC and calculates an optimal fee.
        Returns micro_lamports per compute unit.
        """
        try:
            # Fetch recent fees (looking back 150 slots)
            # Note: get_recent_prioritization_fees takes a list of writable accounts, 
            # passing empty list checks global average which is fine for this use case.
            resp = await self.client.get_recent_prioritization_fees([])
            fees = [x.prioritization_fee for x in resp.value]
            
            if not fees:
                return 5000 # Default to 5000 micro-lamports if no data
            
            # Simple strategy: Take the median or max to ensure inclusion
            # For a "Degen" tool, we want speed, so let's go with a safe high value
            # Sorting and taking the 75th percentile
            fees.sort()
            optimal_fee = fees[int(len(fees) * 0.75)]
            
            # Clamp to a reasonable minimum (e.g. 1000)
            return max(optimal_fee, 1000)
        except Exception as e:
            print(f"⚠️ Failed to fetch priority fees, using default. Error: {e}")
            return 5000 # Fallback

    async def build_transactions(self, instructions: list[Instruction], payer_pubkey: Pubkey) -> list[str]:
        """Builds VALID unsigned transactions with Priority Fees and real blockhash."""
        if not instructions:
            return []

        # 1. Fetch Real Blockhash
        latest_blockhash_resp = await self.client.get_latest_blockhash()
        recent_blockhash = latest_blockhash_resp.value.blockhash

        # 2. Calculate Priority Fee
        priority_fee_micro_lamports = await self.get_optimal_priority_fee()
        print(f"⚡ Agent calculated optimal Priority Fee: {priority_fee_micro_lamports} micro-lamports/CU")

        # 3. Create Compute Budget Instructions
        # Priority Fee Instruction
        priority_fee_ix = set_compute_unit_price(priority_fee_micro_lamports)
        # Compute Unit Limit (Optional, but good practice. Closing accounts is cheap, ~5000 CU)
        # We'll set a safe buffer.
        
        # 4. Batching
        # We can fit about 20-25 close instructions if they are simple, but let's stick to 12 for safety + priority fee overhead
        batch_size = 12
        serialized_txs = []

        for i in range(0, len(instructions), batch_size):
            # Start the batch with the Priority Fee instruction
            batch_ixs = [priority_fee_ix]
            
            # Add the close instructions
            batch_ixs.extend(instructions[i:i + batch_size])
            
            # Create Message
            msg = Message(batch_ixs, payer_pubkey)
            
            # Create Transaction object (Unsigned)
            tx = Transaction([], msg, recent_blockhash)
            
            # Set the fee payer
            tx.fee_payer = payer_pubkey
            
            # Serialize
            tx_bytes = bytes(tx)
            tx_b64 = base64.b64encode(tx_bytes).decode("utf-8")
            serialized_txs.append(tx_b64)

        return serialized_txs
