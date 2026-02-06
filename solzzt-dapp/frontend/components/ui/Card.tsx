"use client";
import { motion } from 'framer-motion';

export const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className={`bg-slate-900/50 backdrop-blur-md border border-green-400/20 rounded-lg p-6 sm:p-8 shadow-2xl shadow-green-500/10 ${className}`}
    >
        {children}
    </motion.div>
);
