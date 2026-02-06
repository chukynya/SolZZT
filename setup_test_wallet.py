import asyncio
import os
import json
import time
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import CreateAccountParams, create_account
from solders.transaction import Transaction
from solders.message import Message
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import initialize_account, InitializeAccountParams

# Constants
RPC_URL = "https://api.devnet.solana.com"
WRAPPED_SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
ACCOUNT_LEN = 165
KEYPAIR_FILE = "test_wallet.json"

async def setup_robust_wallet():
    client = AsyncClient(RPC_URL)
    owner = None

    # 1. Load or Regenerate Wallet (Robustly)
    if os.path.exists(KEYPAIR_FILE):
        try:
            with open(KEYPAIR_FILE, 'r') as f:
                data = json.load(f)
                owner = Keypair.from_bytes(data)
            print(f"📂 Loaded Existing Wallet: {owner.pubkey()}")
        except json.JSONDecodeError:
            print("⚠️ Corrupt/Empty wallet file found. Regenerating...")
            os.remove(KEYPAIR_FILE)
    
    if owner is None:
        owner = Keypair()
        with open(KEYPAIR_FILE, 'w') as f:
            json.dump(list(bytes(owner)), f)
        print(f"🆕 Generated & Saved Wallet: {owner.pubkey()}")
    
    # 2. Check Balance & Pause for Manual Funding
    balance_resp = await client.get_balance(owner.pubkey())
    balance = balance_resp.value
    
    if balance < 1_000_000: # Less than 0.001 SOL
        print("\n" + "!"*60)
        print(f"🛑 ACTION REQUIRED: The Airdrop API is failing (Rate Limits).")
        print(f"   Please fund this address MANUALLY via a Web Faucet:")
        print(f"   👉 Address: {owner.pubkey()}")
        print(f"   👉 URL 1: https://faucet.solana.com/")
        print(f"   👉 URL 2: https://faucet.quicknode.com/solana/devnet")
        print("!"*60)
        
        while True:
            print("⏳ Waiting for funds... (Checking every 10s)")
            await asyncio.sleep(10)
            balance_resp = await client.get_balance(owner.pubkey())
            if balance_resp.value > 10_000_000: # > 0.01 SOL
                print("✅ Funds Received!")
                break
    else:
        print("💰 Wallet is funded. Proceeding...")

    # 3. Create Zombie Account
    # We use a random new keypair for the token account so we don't collide if you run this multiple times
    new_token_account = Keypair()
    rent_resp = await client.get_minimum_balance_for_rent_exemption(ACCOUNT_LEN)
    rent = rent_resp.value
    
    print(f"🧟 Attempting to create Zombie Token Account {new_token_account.pubkey()}...")
    
    try:
        create_ix = create_account(CreateAccountParams(
            from_pubkey=owner.pubkey(),
            to_pubkey=new_token_account.pubkey(),
            lamports=rent,
            space=ACCOUNT_LEN,
            owner=TOKEN_PROGRAM_ID
        ))
        
        init_ix = initialize_account(InitializeAccountParams(
            account=new_token_account.pubkey(),
            mint=WRAPPED_SOL_MINT,
            owner=owner.pubkey(),
            program_id=TOKEN_PROGRAM_ID
        ))
        
        recent_blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        msg = Message([create_ix, init_ix], owner.pubkey())
        tx = Transaction([owner, new_token_account], msg, recent_blockhash)
        
        sig_resp = await client.send_transaction(tx)
        
        # We extract the signature value from the response object
        print(f"   Tx Sent: {sig_resp.value}")
        await client.confirm_transaction(sig_resp.value)
        
        print(f"✅ SUCCESS: Zombie Account Created!")
        print(f"   Token Account: {new_token_account.pubkey()}")
        print(f"   Balance: 0")
    except Exception as e:
        print(f"⚠️ Transaction failed: {e}")
        print("   (If the error says 'Account already in use', just run the script again)")

    await client.close()
    
    print("\n" + "="*40)
    print("🚀 TEST SETUP COMPLETE")
    print(f"Target Public Key: {owner.pubkey()}")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(setup_robust_wallet())
