import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from sqlmodel import Session, select

# Import modules
from app.sniffer import Sniffer
from app.sweeper import Sweeper
from app.database import create_db_and_tables, get_session, Wallet, engine
from app.watcher import Watcher

# --- Configuration ---
RPC_URL = os.getenv("SOLANA_RPC_URL", "https://devnet.helius-rpc.com/?api-key=929876d8-c714-47d1-a1d4-6541ac589e56")

# --- Global State ---
rpc_client: AsyncClient = None
sniffer_instance: Sniffer = None
sweeper_instance: Sweeper = None
watcher_instance: Watcher = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rpc_client, sniffer_instance, sweeper_instance, watcher_instance
    print(f"[Backend] Starting up... Initializing RPC client with {RPC_URL}")
    
    create_db_and_tables()
    
    rpc_client = AsyncClient(RPC_URL)
    sniffer_instance = Sniffer(rpc_client, RPC_URL)
    sweeper_instance = Sweeper(rpc_client)
    
    # Initialize and start Watcher
    watcher_instance = Watcher(sniffer_instance, sweeper_instance)
    # Start the watcher loop as a non-blocking background task
    asyncio.create_task(watcher_instance.start_loop(interval_seconds=60))
    
    yield
    
    # Shutdown
    if watcher_instance:
        watcher_instance.is_running = False
    if rpc_client:
        await rpc_client.close()
        print("[Backend] RPC client closed.")

app = FastAPI(
    title="SolZZT Web3 dApp Backend",
    description="API for the Autonomous Liquidity Recycler (SolZZT)",
    version="1.1.0",
    lifespan=lifespan
)

# --- CORS Configuration ---
origins = ["http://localhost:3000", "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class SniffResponse(BaseModel):
    zombies: List[str]
    total_sol_recoverable: float
    dust: List[dict]
    active: List[dict]

class SweepRequest(BaseModel):
    wallet_address: str
    zombie_accounts: List[str]

class SweepResponse(BaseModel):
    transactions: List[str]

class WatchRequest(BaseModel):
    wallet_address: str
    threshold_sol: float = 0.1

class WatchResponse(BaseModel):
    status: str
    message: str

class WalletStatusResponse(BaseModel):
    address: str
    status: str
    threshold_sol: float
    recoverable_sol: float
    bundle_ready: bool
    bundle_tx: Optional[str] = None

# --- API Endpoints ---

@app.get("/sniff/{wallet_address}", response_model=SniffResponse)
async def sniff_wallet(wallet_address: str):
    try:
        owner_pubkey = Pubkey.from_string(wallet_address)
        results = await sniffer_instance.sniff_accounts(owner_pubkey)
        return SniffResponse(
            zombies=results.get("zombie", []),
            total_sol_recoverable=results.get("total_recoverable_sol", 0.0),
            dust=results.get("dust", []),
            active=results.get("active", [])
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid wallet address: {e}")
    except Exception as e:
        print(f"ERROR: Sniffing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sweep", response_model=SweepResponse)
async def sweep_accounts(request: SweepRequest):
    try:
        owner_pubkey = Pubkey.from_string(request.wallet_address)
        instructions = sweeper_instance.create_close_instructions(request.zombie_accounts, owner_pubkey)
        # Pass owner_pubkey as payer placeholder for unsigned tx
        unsigned_txs_base64 = await sweeper_instance.build_transactions(instructions, owner_pubkey)
        return SweepResponse(transactions=unsigned_txs_base64)
    except Exception as e:
        print(f"ERROR: Sweeping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- New Auto-Maintenance Endpoints ---

@app.post("/watch", response_model=WatchResponse)
async def watch_wallet(request: WatchRequest, session: Session = Depends(get_session)):
    """Registers a wallet for auto-maintenance monitoring."""
    try:
        # Check if already exists
        existing = session.get(Wallet, request.wallet_address)
        if existing:
            existing.threshold_sol = request.threshold_sol
            existing.status = "idle" # Reset status
            session.add(existing)
            msg = f"Updated monitoring for {request.wallet_address}"
        else:
            new_wallet = Wallet(address=request.wallet_address, threshold_sol=request.threshold_sol)
            session.add(new_wallet)
            msg = f"Started monitoring {request.wallet_address}"
        
        session.commit()
        # Trigger an immediate scan in background (optional optimization)
        # asyncio.create_task(watcher_instance.scan_wallets()) 
        return WatchResponse(status="success", message=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/watch/{wallet_address}", response_model=WalletStatusResponse)
async def get_watch_status(wallet_address: str, session: Session = Depends(get_session)):
    """Checks the status of an auto-monitored wallet."""
    wallet = session.get(Wallet, wallet_address)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found in monitoring list")
    
    return WalletStatusResponse(
        address=wallet.address,
        status=wallet.status,
        threshold_sol=wallet.threshold_sol,
        recoverable_sol=wallet.recoverable_sol,
        bundle_ready=(wallet.status == "bundle_ready"),
        bundle_tx=wallet.bundle_base64 if wallet.status == "bundle_ready" else None
    )
