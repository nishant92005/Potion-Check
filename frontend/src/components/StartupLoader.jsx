import { motion } from "framer-motion";
import { PotionIcon } from "./PotionLogo";

const scanLines = [
  "Ingredient matrix online",
  "Allergen vectors mapped",
  "Nutrition model calibrated",
  "AI verdict engine ready"
];

const barcodeBars = [16, 28, 10, 34, 18, 42, 12, 30, 20, 38, 14, 26, 44, 18, 32, 12, 36, 22];

export function StartupLoader({ done = false }) {
  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: done ? 0 : 1 }}
      transition={{ duration: 0.45, ease: "easeInOut" }}
      className="startup-loader fixed inset-0 z-[9999] grid place-items-center overflow-hidden bg-space"
      aria-hidden={done}
    >
      <div className="startup-grid" />
      <div className="startup-aurora" />
      <div className="startup-shell">
        <div className="startup-orbital" aria-hidden="true">
          <div className="startup-ring startup-ring-outer" />
          <div className="startup-ring startup-ring-middle" />
          <div className="startup-ring startup-ring-inner" />
          <div className="startup-scan" />
          <div className="startup-core">
            <PotionIcon className="h-20 w-20 drop-shadow-[0_0_24px_rgba(0,255,178,0.55)]" />
          </div>
          <span className="startup-node startup-node-a" />
          <span className="startup-node startup-node-b" />
          <span className="startup-node startup-node-c" />
          <span className="startup-node startup-node-d" />
        </div>

        <div className="startup-copy">
          <p className="font-mono text-[0.68rem] uppercase tracking-[0.34em] text-mint/80">AI Ingredient Intelligence</p>
          <h1 className="mt-3 font-orbitron text-3xl font-black text-ice sm:text-5xl">
            Potion<span className="text-mint">Check</span>
          </h1>
          <div className="startup-status mt-5">
            {scanLines.map((line, index) => (
              <span key={line} style={{ animationDelay: `${index * 0.38}s` }}>
                {line}
              </span>
            ))}
          </div>
        </div>

        <div className="startup-card" aria-hidden="true">
          <div className="startup-card-top">
            <span />
            <span />
          </div>
          <div className="startup-barcode">
            {barcodeBars.map((height, index) => (
              <i key={index} style={{ height: `${height}px`, animationDelay: `${index * 0.045}s` }} />
            ))}
            <b />
          </div>
          <div className="startup-score">
            <span>SCAN</span>
            <strong>98%</strong>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
