import { motion } from "framer-motion";
import { clsx } from "clsx";

export function GlowButton({ children, className, variant = "primary", onClick, type = "button", disabled }) {
  const base = "relative overflow-hidden rounded-full px-7 py-4 font-orbitron text-sm font-bold transition";
  const styles = variant === "primary"
    ? "bg-gradient-to-r from-mint to-violet text-white shadow-neon animate-pulseGlow hover:from-violet hover:to-mint"
    : "border border-mint text-mint hover:bg-mint/10";
  return (
    <motion.button
      type={type}
      disabled={disabled}
      whileHover={{ scale: disabled ? 1 : 1.03 }}
      whileTap={{ scale: disabled ? 1 : 0.97 }}
      transition={{ type: "spring", stiffness: 420, damping: 24 }}
      onClick={onClick}
      className={clsx(base, styles, disabled && "opacity-60", className)}
    >
      {children}
    </motion.button>
  );
}

export function GlassCard({ children, className, onClick }) {
  return (
    <motion.div
      role={onClick ? "button" : undefined}
      onClick={onClick}
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 280, damping: 22 }}
      className={clsx("glass", onClick && "clickable", className)}
    >
      {children}
    </motion.div>
  );
}

export function Pill({ selected, children, onClick, single }) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
      transition={{ type: "spring", stiffness: 360, damping: 22 }}
      className={clsx(
        "flex min-h-11 items-center gap-2 rounded-full border px-4 py-2 text-sm transition",
        selected ? "border-transparent bg-gradient-to-r from-mint to-violet text-white shadow-neon" : "border-white/10 bg-ocean/70 text-slate hover:border-mint/70 hover:text-ice"
      )}
      aria-pressed={single ? undefined : selected}
    >
      {selected && <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="font-mono">✓</motion.span>}
      {children}
    </motion.button>
  );
}
