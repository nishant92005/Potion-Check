import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { DNAHelix } from "../components/DNAHelix";
import { PageTransition } from "../components/PageTransition";
import { PotionIcon, PotionLogo } from "../components/PotionLogo";
import { GlowButton, GlassCard } from "../components/Interactive";
import { useTypewriter } from "../hooks/useTypewriter";
import { useCountUp } from "../hooks/useCountUp";

function Lettered({ text, from = -20, delay = 0 }) {
  return (
    <span>
      {text.split("").map((char, index) => (
        <motion.span key={`${char}-${index}`} initial={{ opacity: 0, x: from }} animate={{ opacity: 1, x: 0 }} transition={{ delay: delay + index * 0.06 }}>
          {char}
        </motion.span>
      ))}
    </span>
  );
}

function Stat({ target, suffix, label }) {
  const [ref, value] = useCountUp(target);
  return (
    <GlassCard className="p-5 text-center">
      <div className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-full bg-mint/10 text-mint">✦</div>
      <p ref={ref} className="font-orbitron text-3xl font-black text-mint">{value}{suffix}</p>
      <p className="mt-1 text-sm text-slate">{label}</p>
    </GlassCard>
  );
}

function IndianFlag() {
  return (
    <span className="relative h-6 w-9 shrink-0 overflow-hidden rounded-sm border border-white/40 shadow-[0_0_18px_rgba(255,255,255,.16)] sm:h-8 sm:w-12 md:h-10 md:w-16" aria-hidden="true">
      <span className="block h-1/3 bg-[#FF9933]" />
      <span className="relative block h-1/3 bg-white">
        <svg className="absolute left-1/2 top-1/2 h-[9px] w-[9px] -translate-x-1/2 -translate-y-1/2 sm:h-[12px] sm:w-[12px] md:h-[15px] md:w-[15px]" viewBox="0 0 32 32">
          <circle cx="16" cy="16" r="13.5" fill="none" stroke="#000080" strokeWidth="2" />
          <circle cx="16" cy="16" r="2" fill="#000080" />
          {Array.from({ length: 24 }).map((_, index) => (
            <line key={index} x1="16" y1="16" x2="16" y2="3.7" stroke="#000080" strokeWidth="1" transform={`rotate(${index * 15} 16 16)`} />
          ))}
        </svg>
      </span>
      <span className="block h-1/3 bg-[#138808]" />
    </span>
  );
}

function ScanPreview() {
  return (
    <motion.div initial={{ opacity: 0, x: 50, rotateY: -14 }} animate={{ opacity: 1, x: 0, y: [0, -10, 0], rotateY: 0 }} transition={{ opacity: { delay: 0.5, duration: 0.8 }, x: { delay: 0.5, duration: 0.8 }, rotateY: { delay: 0.5, duration: 0.8 }, y: { delay: 1.2, duration: 5, repeat: Infinity, ease: "easeInOut" } }} className="relative mx-auto w-full max-w-sm sm:max-w-md">
      <div className="absolute -inset-4 rounded-[2rem] bg-[conic-gradient(from_180deg,#00FFB2,#FF9933,#7B61FF,#138808,#00FFB2)] opacity-30 blur-2xl" />
      <div className="glass relative overflow-hidden rounded-[2rem] p-4 sm:p-5">
        <motion.span animate={{ x: ["-120%", "120%"] }} transition={{ duration: 4, repeat: Infinity, ease: "linear" }} className="pointer-events-none absolute inset-y-0 w-1/2 -skew-x-12 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="flex items-center justify-between border-b border-mint/15 pb-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.25em] text-mint">Live Scan</p>
            <h3 className="mt-1 font-orbitron text-xl font-black text-ice">Instant Label Report</h3>
          </div>
          <motion.span animate={{ boxShadow: ["0 0 0 rgba(0,255,178,0)", "0 0 24px rgba(0,255,178,.45)", "0 0 0 rgba(0,255,178,0)"] }} transition={{ duration: 2, repeat: Infinity }} className="rounded-full border border-mint/30 bg-mint/10 px-3 py-1 font-mono text-xs text-mint">AI</motion.span>
        </div>
        <div className="relative mt-5 overflow-hidden rounded-2xl border border-mint/20 bg-space/80 p-4 sm:p-5">
          <div className="relative h-24 rounded-xl bg-ice/95 p-4">
            <div className="flex h-full items-end justify-center gap-1">
              {Array.from({ length: 24 }).map((_, i) => <motion.span key={i} animate={{ height: [`${45 + (i * 13) % 42}%`, `${58 + (i * 17) % 36}%`, `${45 + (i * 13) % 42}%`] }} transition={{ duration: 1.8, repeat: Infinity, delay: i * 0.03 }} className="bg-space" style={{ width: `${2 + (i % 5)}px` }} />)}
            </div>
            <motion.span animate={{ x: ["0%", "100%", "0%"] }} transition={{ duration: 2.4, repeat: Infinity, ease: "linear" }} className="absolute inset-y-0 left-0 w-1 bg-mint shadow-neon" />
          </div>
          <div className="mt-5 grid grid-cols-[76px_1fr] gap-3 sm:grid-cols-[92px_1fr] sm:gap-4">
            <motion.div animate={{ scale: [1, 1.04, 1], borderColor: ["rgba(0,255,178,.2)", "rgba(0,255,178,.65)", "rgba(0,255,178,.2)"] }} transition={{ duration: 2.2, repeat: Infinity }} className="grid h-20 place-items-center rounded-2xl border border-mint/20 bg-ocean sm:h-24">
              <motion.span animate={{ opacity: [0.75, 1, 0.75] }} transition={{ duration: 1.6, repeat: Infinity }} className="font-orbitron text-3xl font-black text-mint">86</motion.span>
            </motion.div>
            <div className="space-y-3">
              <motion.div animate={{ width: ["35%", "80%", "80%"] }} transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }} className="h-3 rounded-full bg-mint/70" />
              <motion.div animate={{ width: ["25%", "100%", "100%"] }} transition={{ duration: 2.4, repeat: Infinity, delay: 0.18, ease: "easeInOut" }} className="h-3 rounded-full bg-white/15" />
              <motion.div animate={{ width: ["20%", "66%", "66%"] }} transition={{ duration: 2.4, repeat: Infinity, delay: 0.34, ease: "easeInOut" }} className="h-3 rounded-full bg-white/15" />
              <div className="flex flex-wrap gap-2 pt-1">
                <motion.span animate={{ y: [0, -3, 0] }} transition={{ duration: 2, repeat: Infinity }} className="rounded-full bg-mint/15 px-2.5 py-1 text-xs text-mint">low sugar</motion.span>
                <motion.span animate={{ y: [0, -3, 0] }} transition={{ duration: 2, repeat: Infinity, delay: 0.25 }} className="rounded-full bg-warning/15 px-2.5 py-1 text-xs text-warning">check sodium</motion.span>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-2 text-center sm:gap-3">
          {["Ingredients", "Allergens", "Fitness"].map((item, index) => <motion.div key={item} animate={{ opacity: [0.45, 1, 0.45] }} transition={{ duration: 2.6, repeat: Infinity, delay: index * 0.28 }} className="rounded-2xl border border-white/10 bg-white/[.03] p-3 text-xs text-slate">{item}</motion.div>)}
        </div>
      </div>
    </motion.div>
  );
}

function Feature({ title, text, side, type }) {
  return (
    <motion.section initial={{ opacity: 0, x: side === "left" ? -80 : 80 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, amount: 0.35 }} transition={{ duration: 0.7 }} className="mx-auto grid min-h-[70vh] max-w-6xl items-center gap-10 py-16 md:grid-cols-2">
      <div className={side === "right" ? "md:order-2" : ""}>
        <AnimatedIllustration type={type} />
      </div>
      <div>
        <p className="font-mono text-sm uppercase tracking-[0.35em] text-mint">PotionCheck System</p>
        <h2 className="mt-4 font-orbitron text-3xl font-black md:text-5xl">{title}</h2>
        <p className="mt-5 text-base leading-7 text-slate md:text-lg md:leading-8">{text}</p>
      </div>
    </motion.section>
  );
}

function AnimatedIllustration({ type }) {
  return (
    <GlassCard className="relative h-64 overflow-hidden p-5 sm:h-72 sm:p-8">
      {type === "barcode" && <div className="relative mx-auto mt-10 h-28 w-full max-w-64 rounded-lg border border-mint/30 bg-space/60 p-4 sm:p-5">{Array.from({ length: 18 }).map((_, i) => <span key={i} className="mx-0.5 inline-block h-full bg-ice/80 sm:mx-1" style={{ width: `${2 + (i % 4)}px` }} />)}<span className="absolute left-0 top-0 h-full w-1 bg-mint shadow-neon animate-[scanx_2s_linear_infinite]" /></div>}
      {type === "molecule" && <div className="relative h-full">{Array.from({ length: 8 }).map((_, i) => <motion.span key={i} initial={{ scale: 0 }} whileInView={{ scale: 1 }} transition={{ delay: i * 0.12 }} className="absolute grid h-10 w-10 place-items-center rounded-full bg-gradient-to-r from-mint to-violet shadow-neon" style={{ left: `${15 + (i * 21) % 70}%`, top: `${20 + (i * 37) % 55}%` }} />)}</div>}
      {type === "profile" && <div className="mx-auto mt-4 max-w-xs rounded-3xl border border-mint/20 bg-ocean/70 p-5"><div className="mx-auto h-16 w-16 rounded-full bg-mint/20 animate-float" /><div className="mt-6 space-y-3">{["Gluten", "Diabetes", "Vegan"].map((x) => <div key={x} className="rounded-full bg-gradient-to-r from-mint/40 to-violet/40 px-4 py-3 text-center font-mono text-sm">{x}</div>)}</div></div>}
      <style>{`@keyframes scanx{to{transform:translateX(16rem)}}`}</style>
    </GlassCard>
  );
}

export default function Landing() {
  const typed = useTypewriter([
    "Know Exactly What You Are Eating.",
    "Your Personal AI Food Safety Guardian.",
    "Scan Any Product In Seconds.",
    "Ingredients Decoded For Your Health."
  ]);

  return (
    <PageTransition>
      <section className="relative -mt-24 flex min-h-screen items-center overflow-hidden pb-12 pt-28 md:-mt-28 md:pb-16 md:pt-32">
        <DNAHelix />
        <div className="relative z-10 mx-auto grid max-w-7xl items-center gap-10 px-1 sm:px-5 md:grid-cols-[1.05fr_.95fr] md:gap-12">
          <div className="text-center md:text-left">
            <motion.div initial={{ y: -28, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ type: "spring", stiffness: 200, damping: 15 }} className="mb-7 flex justify-center md:justify-start">
              <PotionIcon className="h-24 w-24" />
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 18, scale: 0.96 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ delay: 0.15, duration: 0.55 }} className="relative inline-flex overflow-hidden rounded-[1.6rem] border border-mint/40 bg-space/80 p-[1px] shadow-[0_0_45px_rgba(0,255,178,.28)] backdrop-blur">
              <span className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,153,51,.45),rgba(255,255,255,.18),rgba(19,136,8,.45))]" />
              <span className="relative flex max-w-[calc(100vw-2rem)] items-center gap-2 rounded-[1.55rem] bg-space/90 px-3 py-3 sm:gap-3 sm:px-4 sm:py-4 md:gap-4 md:px-7">
                <IndianFlag />
                <span className="min-w-0 font-orbitron text-base font-black uppercase leading-tight text-ice drop-shadow-[0_0_16px_rgba(0,255,178,.45)] sm:text-xl md:text-3xl">Label Padhega India</span>
              </span>
            </motion.div>
            <h1 className="mt-5 font-orbitron text-4xl font-black leading-tight sm:text-5xl md:text-8xl">
              <span className="block text-ice"><Lettered text="Potion" /></span>
              <span className="block text-mint"><Lettered text="Check" from={20} delay={0.42} /></span>
            </h1>
            <p className="mt-6 min-h-8 max-w-3xl font-mono text-base text-slate md:text-xl">{typed}<span className="text-mint">|</span></p>
            <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate md:mx-0 md:text-lg md:leading-8">Scan a barcode, decode the label, and get a crisp AI health verdict built for everyday Indian food choices.</p>
            <div className="mt-6 flex flex-wrap justify-center gap-2 md:justify-start">
              {["OpenFoodFacts", "Groq + Ollama", "Health Score", "Daily Limits"].map((chip) => <span key={chip} className="rounded-full border border-white/10 bg-white/[.04] px-3 py-1 text-xs text-slate">{chip}</span>)}
            </div>
            <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.1 }} className="mt-10 flex flex-col justify-center gap-4 sm:flex-row md:justify-start">
              <Link to="/scanner"><GlowButton className="w-full sm:w-auto">Start Scanning Now</GlowButton></Link>
              <Link to="/about"><GlowButton variant="ghost" className="w-full sm:w-auto">See How It Works</GlowButton></Link>
            </motion.div>
          </div>
          <ScanPreview />
          <div className="md:col-span-2">
            <div className="mx-auto grid max-w-5xl gap-4 md:grid-cols-3">
              <Stat target={3} suffix="M+" label="Products in Database" />
              <Stat target={50} suffix="+" label="Allergens Detected" />
              <Stat target={99} suffix="%" label="AI Accuracy Rate" />
            </div>
          </div>
        </div>
        <div className="absolute bottom-8 left-1/2 hidden -translate-x-1/2 text-center text-xs text-slate md:block">
          <div className="mx-auto mb-2 h-10 w-5 rounded-full border border-mint/40"><span className="mx-auto mt-2 block h-1.5 w-1.5 rounded-full bg-mint animate-bounce" /></div>
          Scroll to Explore
        </div>
      </section>
      <Feature type="barcode" side="left" title="Scan Any Product" text="Barcode, label image, pasted text, or fresh produce: every path flows into the same cinematic safety intelligence engine." />
      <Feature type="molecule" side="right" title="AI Ingredient Analysis" text="PotionCheck turns dense ingredient labels into clear ingredient-by-ingredient risk signals with rule checks and Groq-powered reasoning." />
      <Feature type="profile" side="left" title="Personalized Health Alerts" text="Your allergies, conditions, and diet choices shape the final safety report so the verdict is specific to you." />
      <footer className="mx-auto max-w-7xl border-t border-mint/20 px-2 py-10 sm:px-0">
        <div className="flex flex-col justify-between gap-6 md:flex-row">
          <div><PotionLogo /><p className="mt-4 text-sm text-slate">Powered by Ollama, OpenFoodFacts, FSSAI Data, and Tesseract.</p></div>
          <p className="text-sm text-slate">© 2026 PotionCheck. All rights reserved.</p>
        </div>
      </footer>
    </PageTransition>
  );
}
