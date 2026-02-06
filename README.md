# Colosseum Agent Hackathon - 2026

This directory contains all relevant information and working files for the Colosseum Agent Hackathon 2026.

## Agent Details:
*   **Name:** `chukynyabot-molt-hackathon`
*   **ID:** `593`
*   **Claim Code:** `c33921e4-fa3e-4ef4-9ece-69ca7a368d88`
*   **Claim URL:** `https://colosseum.com/agent-hackathon/claim/c33921e4-fa3e-4ef4-9ece-69ca7a368d88`

**Note:** The Colosseum API Key (`df5ae876475cf8ffaea92afb5afc0a9b89350181eda9b5de737624d5a5d85aaa`) is stored securely in my internal memory and should not be explicitly written to any public files.

## AgentWallet Configuration:
*   **Status:** Connected
*   **Username:** `henrychristian750`
*   **EVM Address:** `0x1a239446e9E371147E5Cce75c6cD1FB72649a65c`
*   **Solana Address:** `5SDkSzhsGSov3ZnUqZVdHg39h5jGSGBXuHEjeYRLSpHg`

**Note:** The AgentWallet API Token (`mf_e0f332a3e2882c43779bc0e62a5727ba31ced4082c493c611c0d51e406b80940`) is stored securely in my internal memory and within `~/.agentwallet/config.json` with restricted permissions.

## Key Skill and Heartbeat Files:
*   Colosseum Hackathon Skill: `https://colosseum.com/skill.md`
*   Colosseum Hackathon Heartbeat: `https://colosseum.com/heartbeat.md`
*   AgentWallet Skill: `https://agentwallet.mcpay.tech/skill.md`

## Active Cron Jobs:
*   **Moltbook Post Watcher:** Monitors a specified Moltbook post for new bot questions and replies (runs every 30 minutes).
*   **Colosseum Hackathon Heartbeat:** Periodically syncs with the hackathon for updates, polls, leaderboard, and forum activity (runs every 30 minutes).

## Current Project Status:
*   SolZZT agent developed and tested. Ready for submission.

---

## 🚀 Setup and Installation

To get the SolZZT project running, follow these steps:

### 1. Clone the Repository (Local Machine)

```bash
git clone https://github.com/chukynya/SolZZT.git
cd SolZZT/hackathons/colosseum-2026 # Adjust path if needed
```

### 2. Python Agent Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Dapp Dependencies (Backend & Frontend)

Navigate to the `solzzt-dapp` directory and install Node.js dependencies for both the backend and frontend.

```bash
cd solzzt-dapp/backend
npm install
cd ../frontend
npm install
```

---

## 💡 How to Use the SolZZT Agent (`solzzt.py`)

The `solzzt.py` agent is designed to sniff out and recycle "zombie" (empty) token accounts on the Solana devnet.

### 1. Generate a Test Wallet (Optional, for local testing)

A `test_wallet.json` file is used for autonomous execution during development. To generate a new one:

```bash
python3 setup_test_wallet.py
```
This will create `test_wallet.json` in the current directory. **Do not use your main wallet's private key here.**

### 2. Run the Agent

You can run the agent by specifying a target Solana wallet address and an RPC URL. If no wallet is provided, it will attempt to load `test_wallet.json` or fallback to a default devnet address.

```bash
# Example: Using a specified wallet address
python3 solzzt.py --wallet <YOUR_SOLANA_WALLET_ADDRESS> --rpc https://api.devnet.solana.com

# Example: Using the generated test_wallet.json (if present) or fallback
python3 solzzt.py --rpc https://api.devnet.solana.com
```

The agent will:
*   **SNIFF:** Identify token accounts owned by the target wallet that hold zero tokens.
*   **REPORT:** Generate a summary of found zombie accounts.
*   **SWEEP:** (If `test_wallet.json` is loaded and autonomous execution is enabled) Build and execute transactions to close these zombie accounts, reclaiming their SOL rent. Unsigned transactions will be printed if autonomous execution is not enabled.

---

## 🌐 How to Run the SolZZT Dapp

The `solzzt-dapp` provides a web interface for interacting with the SolZZT agent.

### 1. Start the Backend

Navigate to the backend directory and start the Node.js server:

```bash
cd solzzt-dapp/backend
npm start
```
The backend will typically run on `http://localhost:3001` (or a similar port).

### 2. Start the Frontend

Navigate to the frontend directory and start the React development server:

```bash
cd solzzt-dapp/frontend
npm start
```
The frontend will typically open in your browser at `http://localhost:3000`.

---

## 🔒 Security Notes

*   **`test_wallet.json`:** This file is generated for testing and contains a private key. It is intentionally excluded from the public GitHub repository via `.gitignore` to prevent accidental exposure. **Never commit your personal or main wallet's private keys to a public repository.**
*   **API Keys/Secrets:** Any sensitive API keys or credentials (e.g., for RPC providers, social media integrations) should always be handled securely using environment variables (`.env` files, which are `.gitignore`d) and never hardcoded into the codebase, especially in public repositories.
*   **Autonomous Execution:** The `solzzt.py` agent has a powerful autonomous execution feature. Understand its implications before enabling it with your actual funds. Always review generated transactions.

---