from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solders.instruction import Instruction
from solders.transaction import Transaction
from solders.message import Message
from spl.token.instructions import close_account, CloseAccountParams
from spl.token.constants import TOKEN_PROGRAM_ID
import base64

class Sweeper:
    def __init__(self, client: AsyncClient):
        self.client = client
        print("🧹 Sweeper initialized.")

    def create_close_instructions(self, zombies: list[Pubkey], owner_pubkey: Pubkey) -> list[Instruction]:
        print(f"🔨 Creating close instructions for {len(zombies)} zombie accounts.")
        instructions = []
        for zombie_pubkey in zombies:
            instructions.append(
                close_account(
                    CloseAccountParams(
                        account=zombie_pubkey,
                        dest=owner_pubkey, 
                        owner=owner_pubkey,
                        program_id=TOKEN_PROGRAM_ID
                    )
                )
            )
        return instructions

    async def build_transactions(self, ixs: list[Instruction], owner_keypair: Keypair) -> list[str]:
        print(f"🛠️ Building transactions for {len(ixs)} instructions.")
        unsigned_transactions_base64 = []
        
        if ixs:
            # Fetch a recent blockhash
            latest_blockhash_resp = await self.client.get_latest_blockhash()
            recent_blockhash = latest_blockhash_resp.value.blockhash

            # Create a message with all instructions and the recent blockhash
            message = Message.new_with_blockhash(ixs, owner_keypair.pubkey(), recent_blockhash)
            
            # Create an unsigned transaction by passing the message directly
            transaction = Transaction.new_unsigned(message)
            
            # Encode to base64. Note: This transaction is NOT signed yet.
            # The `execute_recycle` function will sign it later.
            unsigned_transactions_base64.append(base64.b64encode(bytes(transaction)).decode('utf-8'))

        return unsigned_transactions_base64
