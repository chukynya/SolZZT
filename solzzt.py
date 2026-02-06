import asyncio
import argparse
import os
import json
from dotenv import load_dotenv
from solders.pubkey import Pubkey
from solders.keypair import Keypair # Import Keypair
from solana.rpc.async_api import AsyncClient
from solders.transaction import Transaction # Import Transaction for execute_recycle
import base64 # Import base64 for execute_recycle

# Import your modules
from sniffer import Sniffer
from sweeper import Sweeper
from reporter import Reporter

load_dotenv()

# Define the path to the generated test wallet
KEYPAIR_FILE = "test_wallet.json"

async def execute_recycle(tx_base64_list: list[str], signer_keypair: Keypair, client: AsyncClient):
    """Automatically signs and broadcasts the agent's findings."""
    print(f" ⚡ AGENTIC ACTION: Starting Autonomous Recycling...")
    for i, b64_tx in enumerate(tx_base64_list):
        # 1. Reconstruct
        tx_bytes = base64.b64decode(b64_tx)
        tx = Transaction.from_bytes(tx_bytes)

        # Update the blockhash before sending, as it might have changed since building
        latest_blockhash_resp = await client.get_latest_blockhash()
        tx.recent_blockhash = latest_blockhash_resp.value.blockhash

        # Sign the transaction with the loaded keypair
        tx.sign(signer_keypair)

        # 2. Sign and Send
        try:
            sig_resp = await client.send_raw_transaction(bytes(tx))
            await client.confirm_transaction(sig_resp.value)
            print(f"✅ Executed Transaction {i+1}! Rent reclaimed into your wallet.")
            print(f"🔗 View on Solscan: https://solscan.io/tx/{sig_resp.value}?cluster=devnet")
        except Exception as e:
            print(f"❌ Execution failed for Transaction {i+1}: {e}")

async def run_agent(target_wallet_str: str, rpc_url: str):
    print(f"🚀 Starting SolAgent:002 (Target: {target_wallet_str})")
    
    # Initialize Clients
    async with AsyncClient(rpc_url) as client:
        owner_pubkey = Pubkey.from_string(target_wallet_str)

        owner_keypair = None # Initialize owner_keypair for potential autonomous execution
        if os.path.exists(KEYPAIR_FILE):
            try:
                with open(KEYPAIR_FILE, 'r') as f:
                    secret_key_list = json.load(f)
                    owner_keypair = Keypair.from_bytes(bytes(secret_key_list))
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ Error loading keypair from {KEYPAIR_FILE}: {e}. Autonomous execution will not be possible.")
        else:
            print(f"⚠️ {KEYPAIR_FILE} not found. Autonomous execution will not be possible.")

        
        # 1. SNIFF
        sniffer = Sniffer(client, rpc_url)
        results = await sniffer.sniff_accounts(owner_pubkey)
        
        # 2. REPORT
        reporter = Reporter()
        reporter.generate_report(results)
        
        # 3. SWEEP (If Zombies found)
        zombies = results.get("zombie", [])
        if zombies:
            print(f"🧹 Preparing Broom... Found {len(zombies)} accounts to close.")
            sweeper = Sweeper(client)
            
            # Pass the owner_keypair to build_transactions
            if owner_keypair:
                ixs = sweeper.create_close_instructions(zombies, owner_pubkey)
                txs = await sweeper.build_transactions(ixs, owner_keypair) # Pass owner_keypair here
            else:
                print("⚠️ Cannot build transactions: Owner Keypair not loaded. Autonomous execution will not be possible.")
                txs = []
            
            if txs:
                print(f"\n✅ GENERATED {len(txs)} UNSIGNED TRANSACTIONS")
                print("To execute, import these Base64 strings into a wallet or sign script (or enable autonomous execution):")
                for i, tx in enumerate(txs):
                    print(f"\n[TX #{i+1}]: {tx[:50]}... (truncated)")
                    # In a real agent, you might save this to a file: 'tx_queue.json'
                
                # If you want to go Auto-Pilot, call:
                # IMPORTANT: ONLY UNCOMMENT THIS IF YOU UNDERSTAND THE IMPLICATIONS AND TRUST THE AGENT
                if owner_keypair:
                    await execute_recycle(txs, owner_keypair, client)
                else:
                    print("Autonomous execution skipped: Keypair not loaded or provided.")

        else:
            print("✨ Wallet is clean. No zombie accounts found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solana Liquidity Recycler")
    parser.add_argument("--wallet", type=str, help="Target Wallet Address")
    parser.add_argument("--rpc", type=str, default="https://api.devnet.solana.com", help="RPC URL (default to Solana Devnet)") 
    
    args = parser.parse_args()
    
    # Determine the wallet to use
    target_wallet_pubkey_str = args.wallet
    if not target_wallet_pubkey_str:
        # Try to load from test_wallet.json to get the public key
        if os.path.exists(KEYPAIR_FILE):
            try:
                with open(KEYPAIR_FILE, 'r') as f:
                    secret_key_list = json.load(f)
                    owner_keypair_for_pubkey = Keypair.from_bytes(bytes(secret_key_list))
                    target_wallet_pubkey_str = str(owner_keypair_for_pubkey.pubkey())
                print(f"✅ Using wallet from {KEYPAIR_FILE}: {target_wallet_pubkey_str}")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ Error loading wallet public key from {KEYPAIR_FILE}: {e}. Falling back to default test key.")
        
        if not target_wallet_pubkey_str:
            # Fallback to your Devnet testing key for the MVP if file load fails or doesn't exist
            target_wallet_pubkey_str = "5oNDL3swdJJF1g9DzJiZ4ynHXgszjAEpUkxVYejchzrY"
            print(f"⚠️ No wallet provided from CLI or {KEYPAIR_FILE}. Using fallback Test Wallet: {target_wallet_pubkey_str}")

    asyncio.run(run_agent(target_wallet_pubkey_str, args.rpc))
