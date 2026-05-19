import { motion } from "framer-motion";

export function PotionIcon({ className = "h-11 w-11" }) {
  return (
    <motion.svg whileHover={{ scale: 1.06 }} viewBox="0 0 64 64" className={className} aria-hidden="true">
      <defs>
        <linearGradient id="potionLiquid" x1="0" x2="1">
          <stop offset="0%" stopColor="#00FFB2" />
          <stop offset="100%" stopColor="#7B61FF" />
        </linearGradient>
        <clipPath id="flaskClip">
          <path d="M25 7h14v14l13 24c4 7-1 14-9 14H21c-8 0-13-7-9-14l13-24V7Z" />
        </clipPath>
      </defs>
      <path d="M25 7h14v14l13 24c4 7-1 14-9 14H21c-8 0-13-7-9-14l13-24V7Z" fill="rgba(13,27,42,.88)" stroke="#00FFB2" strokeWidth="2" />
      <g clipPath="url(#flaskClip)">
        <motion.path className="animate-liquid" d="M8 41c8-5 14 5 24 0s16-4 24 1v22H8V41Z" fill="url(#potionLiquid)" opacity=".9" />
        {[18, 30, 43].map((cx, index) => (
          <circle key={cx} cx={cx} cy={48 - index * 3} r={2 + index} fill="#E8F4FD" opacity=".55" className="animate-bubble" style={{ animationDelay: `${index * 0.45}s` }} />
        ))}
      </g>
      <rect x="23" y="5" width="18" height="6" rx="2" fill="#0A0F1E" stroke="#7B61FF" />
      <circle cx="51" cy="12" r="5" fill="#00FFB2" className="animate-heartbeat" />
    </motion.svg>
  );
}

export function PotionLogo({ large = false }) {
  return (
    <div className="flex items-center gap-3">
      <PotionIcon className={large ? "h-16 w-16" : "h-11 w-11"} />
      <span className={`${large ? "text-5xl md:text-7xl" : "text-xl"} font-orbitron font-black tracking-normal`}>
        <span className="text-ice">Potion</span><span className="text-mint">Check</span>
      </span>
    </div>
  );
}
