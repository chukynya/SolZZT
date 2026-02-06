from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import Commitment, TokenAccountOpts
import httpx
import json

class Sniffer:
    def __init__(self, client: AsyncClient, rpc_url: str):
        self.client = client
        self.rpc_url = rpc_url
        print(f"✨ Sniffer initialized for RPC: {rpc_url}")

    async def sniff_accounts(self, owner_pubkey: Pubkey) -> dict:
        print(f"🕵️‍♀️ Sniffing accounts for owner: {owner_pubkey}")
        
        zombie_accounts = []
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                str(owner_pubkey),
                {
                    "programId": str(TOKEN_PROGRAM_ID)
                },
                {
                    "encoding": "jsonParsed",
                    "commitment": "confirmed"
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.rpc_url, json=payload)
                response.raise_for_status() # Raise an exception for HTTP errors
                raw_response_json = response.json()
                
                if "result" in raw_response_json and "value" in raw_response_json["result"]:
                    for account_info_raw in raw_response_json["result"]["value"]:
                        account_pubkey_str = account_info_raw["pubkey"]
                        account_data_parsed = account_info_raw["account"]["data"]["parsed"]
                        
                        if 'info' in account_data_parsed and 'tokenAmount' in account_data_parsed['info']:
                            token_amount = account_data_parsed['info']['tokenAmount']
                            if token_amount['amount'] == '0':
                                zombie_accounts.append(Pubkey.from_string(account_pubkey_str))
                                print(f"  Found potential zombie: {account_pubkey_str}")

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during RPC parsing: {e}")
        
        return {"zombie": zombie_accounts}
