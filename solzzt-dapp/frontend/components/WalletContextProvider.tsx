// frontend/components/WalletContextProvider.tsx
"use client";

import React, { useMemo } from 'react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import {
    ConnectionProvider,
    WalletProvider,
} from '@solana/wallet-adapter-react';
import {
    WalletModalProvider,
} from '@solana/wallet-adapter-react-ui';
import {
    PhantomWalletAdapter,
    SolflareWalletAdapter,
    TorusWalletAdapter,
    LedgerWalletAdapter,
} from '@solana/wallet-adapter-wallets';

// It's crucial to require the CSS for the modal to work correctly
require('@solana/wallet-adapter-react-ui/styles.css');

export function WalletContextProvider({ children }: { children: React.ReactNode }) {
    const network = WalletAdapterNetwork.Devnet;

    // Use the Helius RPC from environment variables for stability
    const endpoint = useMemo(() => process.env.NEXT_PUBLIC_SOLANA_RPC_URL || "https://devnet.helius-rpc.com/?api-key=929876d8-c714-47d1-a1d4-6541ac589e56", []);

    const wallets = useMemo(
        () => [
            new PhantomWalletAdapter(),
            new SolflareWalletAdapter(),
            new TorusWalletAdapter(),
            new LedgerWalletAdapter(),
        ],
        [network]
    );

    return (
        <ConnectionProvider endpoint={endpoint}>
            {/* Re-enable autoConnect for a more seamless user experience */}
            <WalletProvider wallets={wallets} autoConnect={true}>
                <WalletModalProvider>{children}</WalletModalProvider>
            </WalletProvider>
        </ConnectionProvider>
    );
}
