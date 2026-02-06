import httpx
import json
import base64
import struct # For parsing byte data
from solana.rpc.async_api import AsyncClient # Use AsyncClient
from solders.pubkey import Pubkey
from solana.exceptions import SolanaRpcException
from solana.rpc.types import TokenAccountOpts # For encoding='jsonParsed'

# Define the SPL Token Program ID once
TOKEN_PROGRAM_ID_STR = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5TT"
TOKEN_PROGRAM_ID_PUBKEY = Pubkey.from_string(TOKEN_PROGRAM_ID_STR)

class Sniffer:
    def __init__(self, rpc_client: AsyncClient, rpc_url: str):
        self.client = rpc_client # Accept and use the AsyncClient
        self.rpc_url = rpc_url # Accept RPC URL string directly
        self.jupiter_price_api = "https://price.jup.ag/v4/price"
        self.rent_exemption_sol = 0.002039

    async def get_token_price(self, mint_address: str) -> float | None:
        """Fetches the price of a token in USD using Jupiter Price API."""
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(f"{self.jupiter_price_api}?ids={mint_address}", timeout=10.0)
                response.raise_for_status()
                data = response.json()
                if data and data.get("data") and data["data"].get(mint_address):
                    return data["data"][mint_address]["price"]
            return None
        except httpx.HTTPStatusError as e:
            print(f"Error fetching price for {mint_address}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Network error fetching price for {mint_address}: {e}")
            return None

    async def sniff_accounts(self, owner_pubkey: Pubkey):
        """
        Scans a Solana wallet for token accounts and categorizes them.
        Returns a dictionary with lists of 'zombie', 'dust', and 'active' accounts.
        """
        accounts = {
            "zombie": [],
            "dust": [],
            "active": [],
            "total_recoverable_sol": 0.0
        }
        
        try:
            all_token_accounts_on_chain = [] # To store all token account data
            try:
                # Set a generous timeout for this potentially very slow call
                timeout = httpx.Timeout(30.0, connect=5.0)
                async with httpx.AsyncClient(timeout=timeout) as http_client:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getProgramAccounts",
                        "params": [
                            TOKEN_PROGRAM_ID_STR,
                            { "encoding": "jsonParsed" }
                        ]
                    }
                    
                    print(f"DEBUG (httpx, getProgramAccounts - ALL): Sending payload...")
                    
                    raw_httpx_response = await http_client.post(self.rpc_url, json=payload)
                    raw_httpx_response.raise_for_status()
                    raw_response_data = raw_httpx_response.json()
                    
                    print(f"DEBUG (httpx, getProgramAccounts - ALL): Successfully received RPC response.")

                    if "error" in raw_response_data:
                        print(f"Solana RPC returned an error in getProgramAccounts (ALL): {raw_response_data['error']}")
                        return accounts

                    if "result" in raw_response_data and isinstance(raw_response_data["result"], list):
                        all_token_accounts_on_chain = raw_response_data["result"]
                    else:
                        print(f"No 'result' list in getProgramAccounts (ALL) response.")
                        return accounts

            except httpx.TimeoutException:
                print("ERROR: The RPC call to getProgramAccounts timed out after 30 seconds. The RPC node may be overloaded.")
                raise # Re-raise the exception to be caught by the main handler
            except httpx.HTTPStatusError as e:
                print(f"HTTP error during raw RPC call getProgramAccounts (ALL): {e.response.status_code} - {e.response.text}")
                return accounts
            except Exception as e:
                print(f"Unexpected error during raw RPC call getProgramAccounts (ALL): {type(e).__name__} - {e}")
                return accounts
            
            if not all_token_accounts_on_chain:
                print(f"No SPL Token accounts found on chain via getProgramAccounts (ALL).")
                return accounts

            # Now, filter client-side for accounts owned by our owner_pubkey
            print(f"DEBUG: Filtering {len(all_token_accounts_on_chain)} SPL Token accounts client-side for owner {owner_pubkey}...")
            for account_item in all_token_accounts_on_chain:
                try:
                    account_data = account_item.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
                    account_owner_str = account_data.get("owner")
                    
                    if account_owner_str == str(owner_pubkey):
                        account_address = Pubkey.from_string(account_item["pubkey"])
                        mint = Pubkey.from_string(account_data["mint"])
                        balance_ui = float(account_data["tokenAmount"]["uiAmount"])
                        
                        if balance_ui == 0:
                            accounts["zombie"].append(str(account_address))
                            accounts["total_recoverable_sol"] += self.rent_exemption_sol
                        else:
                            # Classify as active for now, skip dust check to speed up debugging
                            accounts["active"].append({ "address": str(account_address), "balance": balance_ui })

                except (KeyError, TypeError) as e:
                    # These errors are expected for accounts with different structures, so we can ignore them
                    pass 
        except Exception as e:
            print(f"An unexpected error occurred during sniffing: {type(e).__name__} - {e}")
        
        return accounts

async def main():
    rpc_client_for_test = AsyncClient("https://devnet.helius-rpc.com/?api-key=929876d8-c714-47d1-a1d4-6541ac589e56")
    sniffer = Sniffer(rpc_client_for_test, "https://devnet.helius-rpc.com/?api-key=929876d8-c714-47d1-a1d4-6541ac589e56")
    owner_pubkey_str = "EiWfGmGbEqQJNPjbvuGmivXVSvrkftiVokgyqVbb6abM" 
    owner_pubkey = Pubkey.from_string(owner_pubkey_str)
    
    print(f"Sniffing accounts for {owner_pubkey}...")
    results = await sniffer.sniff_accounts(owner_pubkey)
    
    print(f"Zombie Accounts ({len(results['zombie'])}): {results['zombie']}")
    print(f"Dust Accounts ({len(results['dust'])}): {results['dust']}")
    print(f"Active Accounts ({len(results['active'])}): {results['active']}")
    print(f"Total potential SOL to recover: {results['total_recoverable_sol']:.6f} SOL")
    await rpc_client_for_test.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())