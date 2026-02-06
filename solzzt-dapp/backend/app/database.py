from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional

# --- Database Model ---
class Wallet(SQLModel, table=True):
    address: str = Field(primary_key=True, index=True)
    threshold_sol: float = Field(default=0.1)
    status: str = Field(default="idle") # idle, scanning, bundle_ready
    last_scanned_at: Optional[float] = None
    recoverable_sol: float = Field(default=0.0)
    bundle_base64: Optional[str] = None # Stores the ready-to-sign bundle if threshold met

# --- Database Setup ---
sqlite_file_name = "wallets.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
