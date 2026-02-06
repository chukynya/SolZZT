import type { Metadata } from "next"
import { Inter, IBM_Plex_Mono } from "next/font/google"
import "./globals.css" // Your global styles
import '@solana/wallet-adapter-react-ui/styles.css'; // Wallet adapter styles

import { WalletContextProvider } from '../components/WalletContextProvider';
import { Toaster } from 'sonner';

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-plex-mono",
})

export const metadata: Metadata = {
  title: "SolZZT - The Degen Liquidity Recycler",
  description: "Autonomously clean up zombie and dust token accounts on Solana.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${plexMono.variable} font-sans`}>
        <WalletContextProvider>
          {children}
          <Toaster position="bottom-right" theme="dark" />
        </WalletContextProvider>
      </body>
    </html>
  )
}
