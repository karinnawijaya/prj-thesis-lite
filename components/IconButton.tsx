"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: ReactNode;
  label: string;
}

export function IconButton({ icon, label, className = "", ...props }: IconButtonProps) {
  return (
    <button
      type="button"
      aria-label={label}
      className={`flex h-11 w-11 items-center justify-center rounded-full border border-white/70 bg-white/80 text-slate-700 shadow-soft transition hover:scale-105 hover:bg-white ${className}`}
      {...props}
    >
      {icon}
    </button>
  );
}