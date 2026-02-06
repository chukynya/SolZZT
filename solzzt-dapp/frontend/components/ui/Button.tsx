"use client";
import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface ButtonProps {
    onClick: () => void;
    children: ReactNode;
    disabled?: boolean;
    className?: string;
}

export const Button = ({ onClick, children, disabled = false, className = '' }: ButtonProps) => (
    <motion.button 
        onClick={onClick} 
        disabled={disabled}
        whileHover={{ scale: disabled ? 1 : 1.05 }}
        whileTap={{ scale: disabled ? 1 : 0.95 }}
        className={`w-full py-3 px-4 rounded-lg font-bold text-lg text-slate-900 bg-green-400
                   shadow-lg shadow-green-500/20
                   hover:bg-green-300 hover:shadow-xl hover:shadow-green-400/40
                   transition-all duration-300 ease-in-out
                   disabled:bg-slate-700 disabled:text-slate-500 disabled:shadow-none disabled:cursor-not-allowed
                   ${className}`}
    >
        {children}
    </motion.button>
);
