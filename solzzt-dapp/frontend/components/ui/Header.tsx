"use client";
import Link from 'next/link';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';

export const Header = () => (
    <header className="absolute top-0 left-0 right-0 p-4 sm:p-6 flex justify-between items-center z-20">
        <div className="flex items-center gap-6">
            <Link href="/" className="font-mono text-2xl font-bold text-white tracking-widest hover:opacity-80 transition-opacity">
                Sol<span className="text-green-400">ZZ</span>T
            </Link>
            <Link href="/docs" className="text-sm text-slate-400 hover:text-green-400 transition-colors font-mono">
                Documentation
            </Link>
        </div>
        <WalletMultiButton style={{ 
            backgroundColor: 'rgba(15, 23, 42, 0.5)', // slate-900 with transparency
            border: '1px solid rgba(74, 222, 128, 0.2)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.2s ease-in-out',
        }} />
    </header>
);
