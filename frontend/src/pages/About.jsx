import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { GlassCard } from "../components/Interactive";

const steps = [
  ["01", "Scan or Enter Your Product", "Use barcode scanning, OCR label upload, pasted text, or fresh produce selection."],
  ["02", "AI Analyzes Every Ingredient", "Groq AI and safety rules examine ingredients, allergens, additives, and nutrition signals."],
  ["03", "Get Your Personalized Safety Report", "The final report is tuned to your allergies, diet, and health conditions."]
];

export default function About() {
  return (
    <PageTransition>
      <div className="mx-auto max-w-6xl">
        <h1 className="font-orbitron text-3xl font-black md:text-6xl">How PotionCheck Works</h1>
        <div className="mt-12 space-y-20">
          {steps.map(([num, title, text], index) => (
            <motion.section key={num} initial={{ opacity: 0, y: 60 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.35 }} className="grid min-h-[55vh] items-center gap-8 md:grid-cols-2">
              <GlassCard className={`h-60 overflow-hidden p-5 sm:h-72 sm:p-8 ${index % 2 ? "md:order-2" : ""}`}>
                <svg viewBox="0 0 360 220" className="h-full w-full"><circle cx="180" cy="110" r="74" fill="none" stroke="#00FFB2" strokeDasharray="10 8"><animateTransform attributeName="transform" type="rotate" from="0 180 110" to="360 180 110" dur="8s" repeatCount="indefinite" /></circle><path d="M100 150c50-80 110 80 160-20" fill="none" stroke="#7B61FF" strokeWidth="8" strokeLinecap="round" /><circle cx="120" cy="90" r="14" fill="#00FFB2" /><circle cx="230" cy="125" r="18" fill="#7B61FF" /></svg>
              </GlassCard>
              <div><p className="font-orbitron text-6xl font-black text-mint/30 md:text-8xl">{num}</p><h2 className="font-orbitron text-2xl font-bold md:text-3xl">{title}</h2><p className="mt-5 text-base leading-7 text-slate md:text-lg md:leading-8">{text}</p></div>
            </motion.section>
          ))}
        </div>
        <GlassCard className="mt-10 p-8">
          <h2 className="font-orbitron text-2xl font-bold">Technology Credits</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-4">{["Ollama", "OpenFoodFacts", "FSSAI", "Tesseract"].map((tech) => <div key={tech} className="rounded-2xl border border-mint/15 bg-ocean/60 p-5 text-center font-orbitron">{tech}</div>)}</div>
        </GlassCard>
      </div>
    </PageTransition>
  );
}
