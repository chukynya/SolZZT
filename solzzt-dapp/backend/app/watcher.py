import asyncio
import time
from sqlmodel import Session, select
from solders.pubkey import Pubkey
from app.database import Wallet, engine
from app.sniffer import Sniffer
from app.sweeper import Sweeper

class Watcher:
    def __init__(self, sniffer: Sniffer, sweeper: Sweeper):
        self.sniffer = sniffer
        self.sweeper = sweeper
        self.is_running = False

    async def start_loop(self, interval_seconds: int = 60):
        """Starts the background monitoring loop."""
        self.is_running = True
        print(f"👁️ Auto-Maintenance Watcher started. Scanning every {interval_seconds}s...")
        while self.is_running:
            await self.scan_wallets()
            await asyncio.sleep(interval_seconds)

    async def scan_wallets(self):
        """Iterates through all watched wallets and checks for threshold breaches."""
        with Session(engine) as session:
            statement = select(Wallet)
            wallets = session.exec(statement).all()
            
            for wallet in wallets:
                try:
                    # Skip if already ready (waiting for user action)
                    if wallet.status == "bundle_ready":
                        continue

                    print(f"🔍 [Watcher] Scanning {wallet.address}...")
                    owner_pubkey = Pubkey.from_string(wallet.address)
                    
                    # 1. Sniff
                    results = await self.sniffer.sniff_accounts(owner_pubkey)
                    recoverable = results.get("total_recoverable_sol", 0.0)
                    zombies = results.get("zombie", [])

                    # Update stats
                    wallet.last_scanned_at = time.time()
                    wallet.recoverable_sol = recoverable
                    
                    # 2. Check Threshold
                    if recoverable >= wallet.threshold_sol and len(zombies) > 0:
                        print(f"🚨 [Watcher] Threshold triggered for {wallet.address}! ({recoverable} >= {wallet.threshold_sol})")
                        
                        # 3. Auto-Sweep (Prepare Bundle)
                        ixs = self.sweeper.create_close_instructions(zombies, owner_pubkey)
                        # Note: We need a payer for the transaction. In this autonomous mode, 
                        # we assume the user will sign, so we use their pubkey as payer placeholder.
                        txs = await self.sweeper.build_transactions(ixs, owner_pubkey)
                        
                        # Store the first transaction as the bundle (MVP simplification)
                        if txs:
                            wallet.bundle_base64 = txs[0] 
                            wallet.status = "bundle_ready"
                    else:
                        wallet.status = "idle"
                        wallet.bundle_base64 = None
                    
                    session.add(wallet)
                    session.commit()
                    
                except Exception as e:
                    print(f"❌ [Watcher] Error scanning {wallet.address}: {e}")
