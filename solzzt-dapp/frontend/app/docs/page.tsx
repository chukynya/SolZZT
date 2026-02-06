// frontend/app/docs/page.tsx
"use client";

import { Header } from "@/components/ui/Header";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, BrainCircuit, ShieldCheck, Zap, Bot, Target, HelpCircle } from "lucide-react";

const Section = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <motion.section 
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className={`py-12 border-b border-white/10 ${className}`}
    >
        {children}
    </motion.section>
);

const DocsPage = () => {
    return (
        <div className="relative min-h-screen w-full bg-slate-900 text-slate-200 flex flex-col items-center p-4 font-mono overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full animate-aurora bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops)),radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-green-900/30 via-slate-900 to-slate-900 opacity-50"></div>
            <Header />
            <main className="w-full max-w-4xl mt-24 sm:mt-28 z-10 px-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <Link href="/" className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 transition-colors mb-8">
                        <ArrowLeft size={18} />
                        Back to App
                    </Link>
                    
                    <div className="text-center mb-16">
                        <h1 className="text-6xl font-bold text-white tracking-tighter">
                            The Sol<span className="text-green-400">ZZ</span>T Protocol
                        </h1>
                        <p className="text-slate-400 text-xl mt-4">
                            <strong className="text-white">Sol</strong>ana <strong className="text-white">Z</strong>ero-<strong>Z</strong>one <strong className="text-white">T</strong>rashcollector
                        </p>
                    </div>

                    <Section>
                        <div className="grid md:grid-cols-2 gap-8 items-center">
                            <div>
                                <h2 className="text-3xl font-bold text-white mb-3 flex items-center gap-3"><HelpCircle className="text-green-400" /> What is SolZZT?</h2>
                                <p className="text-slate-400 text-lg leading-relaxed">
                                    SolZZT is an autonomous agentic protocol designed to reclaim trapped liquidity on the Solana blockchain. It functions as a "Degen Janitor," intelligently scanning wallets to find and close unused token accounts, returning the locked SOL rent directly to you.
                                </p>
                            </div>
                            <div className="text-center">
                                <Bot size={80} className="text-green-400 inline-block" />
                            </div>
                        </div>
                    </Section>

                    <Section>
                        <div className="grid md:grid-cols-2 gap-8 items-center">
                             <div className="text-center">
                                <Target size={80} className="text-red-400 inline-block" />
                            </div>
                            <div>
                                <h2 className="text-3xl font-bold text-white mb-3">The Problem: "State Noise"</h2>
                                <p className="text-slate-400 text-lg leading-relaxed">
                                    Every new SPL token requires a dedicated account that locks ~0.002 SOL as rent. For active traders, this results in hundreds of old, empty "zombie" accounts, collectively trapping a significant amount of SOL. This is unproductive capital and blockchain bloat.
                                </p>
                            </div>
                        </div>
                    </Section>

                    <Section>
                        <div className="grid md:grid-cols-2 gap-8 items-center">
                            <div>
                                <h2 className="text-3xl font-bold text-white mb-3">The Solution: Agentic Recycling</h2>
                                <p className="text-slate-400 text-lg leading-relaxed">
                                    SolZZT's agent analyzes your wallet to distinguish between valuable accounts and worthless "zombies." It then prepares the exact instructions needed to close the zombie accounts and bundles them for your approval, turning digital trash back into liquid capital.
                                </p>
                            </div>
                             <div className="text-center">
                                <Zap size={80} className="text-yellow-400 inline-block" />
                            </div>
                        </div>
                    </Section>

                     <Section className="border-none">
                        <div className="grid md:grid-cols-2 gap-8 items-center">
                             <div className="text-center">
                                <ShieldCheck size={80} className="text-blue-400 inline-block" />
                            </div>
                            <div>
                                <h2 className="text-3xl font-bold text-white mb-3">Security Protocol</h2>
                                <p className="text-slate-400 text-lg leading-relaxed">
                                    Your security is the priority. The agent only builds <strong className="text-white">unsigned transactions</strong>. It never sees your private keys. You give the final, explicit approval by signing with your own secure wallet.
                                </p>
                            </div>
                        </div>
                    </Section>
                    
                    <div className="mt-20 text-center text-slate-500">
                        <p>SolZZT // Colosseum Hackathon Entry // Agentic Protocol v1.0</p>
                    </div>

                </motion.div>
            </main>
        </div>
    );
};

export default DocsPage;
