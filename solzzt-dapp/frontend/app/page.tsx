// frontend/app/page.tsx
"use client";

import { useState, useEffect, useMemo } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { Connection, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { toast } from 'sonner';
import { ScanLine, Trash2, Zap, AlertTriangle, Eye, Activity } from 'lucide-react'; // Added icons
import { AnimatePresence, motion } from 'framer-motion';

// --- Re-architected UI Components ---
import { Header } from '@/components/ui/Header';

const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl shadow-green-500/10 ${className}`}>
        {children}
    </div>
);

const Button = ({ onClick, children, disabled = false, className = '' }: { onClick: () => void; children: React.ReactNode; disabled?: boolean; className?: string; }) => (
    <motion.button
        onClick={onClick}
        disabled={disabled}
        whileHover={{ scale: disabled ? 1 : 1.03 }}
        whileTap={{ scale: disabled ? 1 : 0.98 }}
        className={`relative overflow-hidden w-full py-4 px-6 rounded-lg font-bold text-lg text-white bg-green-500/80
                   border border-green-400/50
                   shadow-lg shadow-green-500/20
                   hover:bg-green-400/80 hover:shadow-xl hover:shadow-green-400/40
                   transition-all duration-300 ease-in-out
                   disabled:bg-slate-700 disabled:text-slate-500 disabled:shadow-none disabled:cursor-not-allowed
                   ${className}`}
    >
        <span className="relative z-10">{children}</span>
    </motion.button>
);

const LoadingIndicator = ({ text }: { text: string }) => (
    <div className="flex flex-col items-center justify-center space-y-4 p-8 text-center">
        <motion.div
            className="h-16 w-16"
            animate={{ rotate: 360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        >
            <ScanLine className="h-16 w-16 text-green-400" />
        </motion.div>
        <p className="font-mono text-green-400 animate-pulse">{text}</p>
    </div>
);

// --- Configuration ---
const RPC_URL = process.env.NEXT_PUBLIC_SOLANA_RPC_URL || "https://devnet.helius-rpc.com/?api-key=929876d8-c714-47d1-a1d4-6541ac589e56";
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

// --- Main Page Component ---
export default function HomePage() {
    const [isMounted, setIsMounted] = useState(false);
    useEffect(() => { setIsMounted(true); }, []);

    const { publicKey, connected, signAllTransactions, signTransaction } = useWallet();
    const [isLoading, setIsLoading] = useState(false);
    const [scanState, setScanState] = useState<'idle' | 'scanning' | 'scanned'>('idle');
    const [scanResults, setScanResults] = useState<{ zombies: string[], dust: any[], total_sol_recoverable: number } | null>(null);
    
    // Auto-Maintenance State
    const [watchThreshold, setWatchThreshold] = useState(0.1);
    const [watchStatus, setWatchStatus] = useState<any>(null);

    const connection = useMemo(() => new Connection(RPC_URL, 'confirmed'), []);

    const reset = () => {
        setScanState('idle');
        setScanResults(null);
    };

    const handleScanWallet = async () => {
        if (!publicKey) return;
        setIsLoading(true);
        setScanState('scanning');
        toast.info("Agent dispatched to scan wallet...");

        try {
            const response = await axios.get(`${BACKEND_URL}/sniff/${publicKey.toBase58()}`);
            setScanResults(response.data);
            setScanState('scanned');
            if (response.data.zombies.length === 0 && response.data.dust.length === 0) {
                toast.success("Agent confirms your wallet is clean.");
            } else {
                toast.success(`Agent found ${response.data.zombies.length} zombie accounts.`);
            }
        } catch (error: any) {
            toast.error(`Agent scan failed: ${error.response?.data?.detail || error.message}`);
            reset();
        } finally {
            setIsLoading(false);
        }
    };

    const handleRecycleFunds = async () => {
        if (!publicKey || !signAllTransactions || !scanResults || scanResults.zombies.length === 0) return;
        setIsLoading(true);
        toast.info("Agent is building recycling transactions...");

        try {
            const sweepResponse = await axios.post(`${BACKEND_URL}/sweep`, { wallet_address: publicKey.toBase58(), zombie_accounts: scanResults.zombies });
            const transactions = sweepResponse.data.transactions.map((b64Tx: string) => Transaction.from(Buffer.from(b64Tx, 'base64')));
            
            toast.info("Please approve transactions in your wallet...");
            const signedTransactions = await signAllTransactions(transactions);
            
            toast.info(`Broadcasting ${signedTransactions.length} transactions to the network...`);
            await Promise.all(signedTransactions.map(async (signedTx) => {
                const signature = await connection.sendRawTransaction(signedTx.serialize());
                await connection.confirmTransaction(signature, 'processed');
                return signature;
            }));
            
            toast.success(`✅ Success! ${scanResults.total_sol_recoverable.toFixed(6)} SOL reclaimed.`);
            setTimeout(() => reset(), 2000);
        } catch (error: any) {
            toast.error(`Recycling failed: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    // --- Auto-Maintenance Handlers ---
    const handleStartWatch = async () => {
        if (!publicKey) return;
        try {
            await axios.post(`${BACKEND_URL}/watch`, { 
                wallet_address: publicKey.toBase58(), 
                threshold_sol: watchThreshold 
            });
            toast.success(`Agent is now watching for > ${watchThreshold} SOL recoverable.`);
            fetchWatchStatus();
        } catch (error: any) {
            toast.error(`Failed to start watching: ${error.message}`);
        }
    };

    const fetchWatchStatus = async () => {
        if (!publicKey) return;
        try {
            const res = await axios.get(`${BACKEND_URL}/watch/${publicKey.toBase58()}`);
            setWatchStatus(res.data);
        } catch (e) {
            setWatchStatus(null);
        }
    };

    // Poll watch status if connected
    useEffect(() => {
        if (connected && publicKey) {
            fetchWatchStatus();
            const interval = setInterval(fetchWatchStatus, 10000); // Poll every 10s
            return () => clearInterval(interval);
        }
    }, [connected, publicKey]);

    const handleExecuteBundle = async () => {
        if (!publicKey || !watchStatus?.bundle_tx || !signTransaction) return;
        
        try {
            const tx = Transaction.from(Buffer.from(watchStatus.bundle_tx, 'base64'));
            const signedTx = await signTransaction(tx);
            const sig = await connection.sendRawTransaction(signedTx.serialize());
            await connection.confirmTransaction(sig, 'processed');
            toast.success("✅ Auto-Bundle executed successfully!");
            fetchWatchStatus(); // Refresh status
        } catch (error: any) {
            toast.error(`Bundle execution failed: ${error.message}`);
        }
    };


    useEffect(() => { if (!connected) reset(); }, [connected]);

    if (!isMounted) return null;

    return (
        <div className="relative min-h-screen w-full bg-slate-900 text-slate-200 flex flex-col items-center justify-center p-4 font-mono overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full animate-aurora bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops)),radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-green-900/30 via-slate-900 to-slate-900 opacity-50"></div>
            <Header />
            <main className="w-full max-w-2xl mt-20 z-10 space-y-8">
                
                {/* Main Scanner Card */}
                <Card>
                    <AnimatePresence mode="wait">
                        {!connected ? (
                            <motion.div key="connect" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center p-8">
                                <h1 className="text-5xl font-bold text-white mb-3">Reclaim Your SOL</h1>
                                <p className="text-slate-400 text-lg">Let an autonomous agent find and recycle your trapped liquidity.</p>
                            </motion.div>
                        ) : (
                            <div className="p-4">
                                {scanState === 'idle' && (
                                    <motion.div key="scan" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                                        <div className="text-center mb-6">
                                            <h2 className="text-2xl font-bold text-white">Manual Scan</h2>
                                            <p className="text-slate-400 text-sm">One-time check for zombie accounts.</p>
                                        </div>
                                        <Button onClick={handleScanWallet} disabled={isLoading}>
                                            <div className="flex items-center justify-center gap-2">
                                                <ScanLine /><span>Scan Wallet</span>
                                            </div>
                                        </Button>
                                    </motion.div>
                                )}

                                {scanState === 'scanning' && <motion.div key="scanning"><LoadingIndicator text="Agent analyzing on-chain data..." /></motion.div>}
                                
                                {scanState === 'scanned' && scanResults && (
                                    <motion.div key="results" className="space-y-6">
                                        {(scanResults.zombies.length > 0 || scanResults.dust.length > 0) ? (
                                            <>
                                                {scanResults.zombies.length > 0 && (
                                                    <div className="bg-slate-800/50 p-4 rounded-lg border border-green-500/20">
                                                        <h3 className="font-bold text-lg text-red-400 flex items-center gap-2"><Trash2 size={18} /> Zombie Accounts ({scanResults.zombies.length})</h3>
                                                        <p className="mt-2 text-3xl font-bold text-green-400">{scanResults.total_sol_recoverable.toFixed(6)} SOL</p>
                                                        <p className="text-slate-400 text-sm">Can be instantly reclaimed.</p>
                                                    </div>
                                                )}
                                                {scanResults.zombies.length > 0 && (
                                                    <Button onClick={handleRecycleFunds} disabled={isLoading}>
                                                        <div className="flex items-center justify-center gap-2">
                                                            <Zap /><span>Recycle Now</span>
                                                        </div>
                                                    </Button>
                                                )}
                                            </>
                                        ) : (
                                            <p className="text-center text-green-400 p-4">✨ Agent confirms your wallet is clean!</p>
                                        )}
                                        <Button onClick={reset} disabled={isLoading} className="bg-slate-700/50 text-slate-300 hover:bg-slate-600/50">Scan Again</Button>
                                    </motion.div>
                                )}
                            </div>
                        )}
                    </AnimatePresence>
                </Card>

                {/* Auto-Maintenance Card */}
                {connected && (
                    <Card className="border-t-4 border-t-purple-500">
                        <div className="p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <Eye className="text-purple-400" />
                                <h2 className="text-xl font-bold text-white">Auto-Maintenance</h2>
                            </div>
                            
                            {!watchStatus ? (
                                <div className="space-y-4">
                                    <p className="text-slate-400 text-sm">
                                        Activate the agent to watch your wallet 24/7. It will prepare a recycling bundle automatically when trapped SOL exceeds your threshold.
                                    </p>
                                    <div className="flex gap-4 items-center">
                                        <div className="flex-1">
                                            <label className="text-xs text-slate-500 block mb-1">Threshold (SOL)</label>
                                            <input 
                                                type="number" 
                                                step="0.01"
                                                value={watchThreshold}
                                                onChange={(e) => setWatchThreshold(parseFloat(e.target.value))}
                                                className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white focus:border-purple-500 outline-none transition-colors"
                                            />
                                        </div>
                                        <button 
                                            onClick={handleStartWatch}
                                            className="bg-purple-600 hover:bg-purple-500 text-white font-bold py-3 px-6 rounded-lg transition-colors mt-5"
                                        >
                                            Start Watching
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center bg-slate-900/50 p-3 rounded border border-purple-500/30">
                                        <div className="flex items-center gap-2">
                                            <Activity className="text-green-400 animate-pulse" size={16} />
                                            <span className="text-green-400 font-bold text-sm">Agent Active</span>
                                        </div>
                                        <div className="text-xs text-slate-400">
                                            Threshold: {watchStatus.threshold_sol} SOL
                                        </div>
                                    </div>

                                    {watchStatus.bundle_ready ? (
                                        <div className="bg-purple-900/20 p-4 rounded border border-purple-500 animate-pulse">
                                            <h3 className="text-purple-300 font-bold mb-2">🚨 Recycling Bundle Ready!</h3>
                                            <p className="text-sm text-slate-300 mb-4">
                                                Agent found {watchStatus.recoverable_sol.toFixed(6)} SOL.
                                            </p>
                                            <Button onClick={handleExecuteBundle} className="bg-purple-600 hover:bg-purple-500 border-none shadow-purple-500/20">
                                                Approve & Recycle
                                            </Button>
                                        </div>
                                    ) : (
                                        <p className="text-center text-slate-500 text-sm py-2">
                                            Monitoring... No threshold breach yet.
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    </Card>
                )}

            </main>
        </div>
    );
}
