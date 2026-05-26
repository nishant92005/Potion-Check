import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { DNASpinner } from "../components/DNASpinner";
import { GlowButton, GlassCard } from "../components/Interactive";
import { PotionIcon } from "../components/PotionLogo";
import { analysisService } from "../services/analysisService";
import { useProfileStore, useScanStore, useUIStore } from "../stores/useStores";

const fallback = {
  product_name: "Demo Product Report",
  brand: "PotionCheck",
  barcode: "TEXT",
  categories: ["AI analysis", "ingredient safety"],
  safety_score: 74,
  health_score_out_of_10: 7.4,
  verdict: "CAUTION",
  flagged_ingredients: [{ name: "Artificial flavor", scientific_name: "Flavoring compound", severity: "medium", reason: "May be unsuitable for sensitive profiles.", personalized_warning: "Review this ingredient against your saved conditions." }],
  all_ingredients: [
    { name: "Sugar", status: "caution", why_this_matters: "No direct allergy conflict was detected, but sugar matters for daily energy balance. Globally, added sugar is mainly useful for quick energy and sweetness, while frequent high intake can work against dental, weight, and blood-sugar goals." },
    { name: "Cocoa", status: "safe", why_this_matters: "No direct conflict with your saved profile was detected. Cocoa can add flavor and plant compounds, but cocoa-based packaged foods may still add calories when paired with sugar and fat." },
    { name: "Milk powder", status: "safe", why_this_matters: "No direct conflict with your saved profile was detected. Milk powder can add protein, calcium, and creamy texture, though frequent intake may be unsuitable for people sensitive to dairy or products high in saturated fat." },
    { name: "Artificial flavor", status: "avoid", why_this_matters: "Review this ingredient against your saved conditions. Artificial flavor mainly improves taste without meaningful nutrition, and frequent intake can increase reliance on ultra-processed foods." }
  ],
  nutriments: { carbohydrates_100g: 52, proteins_100g: 6, fat_100g: 22, sugars_100g: 38, sodium_100g: 0.18, fiber_100g: 3 },
  daily_frequency_advice: "Avoid daily use because sugar is high.",
  weekly_frequency_advice: "Keep it to 1 to 2 times per week in a small portion.",
  ai_summary: "PotionCheck found a mostly conventional ingredient profile with one medium-risk flag. The product may be acceptable occasionally, but it is not the cleanest option for a sensitive health profile.",
  ai_recommendation: "Pick a product with fewer additives and lower sugar when available."
};

function scoreColor(score) {
  if (score >= 80) return "#00FFB2";
  if (score >= 50) return "#FFA500";
  return "#FF4560";
}

function SafetyMeter({ score, verdict, label = "HEALTH SCORE" }) {
  const color = scoreColor(score);
  const radius = 92;
  const circumference = 2 * Math.PI * radius;
  return (
    <div className="text-center">
      <svg viewBox="0 0 220 220" className="mx-auto h-48 w-48 max-w-full drop-shadow-[0_0_20px_var(--glow)] sm:h-[220px] sm:w-[220px]" style={{ "--glow": color }}>
        <circle cx="110" cy="110" r={radius} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="16" />
        <motion.circle cx="110" cy="110" r={radius} fill="none" stroke={color} strokeWidth="16" strokeLinecap="round" strokeDasharray={circumference} initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset: circumference - (score / 100) * circumference }} transition={{ duration: 1.8, ease: "easeOut" }} transform="rotate(-90 110 110)" />
        <motion.text x="110" y="112" textAnchor="middle" fill="#E8F4FD" className="font-orbitron text-[52px] font-black" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{score}</motion.text>
        <text x="110" y="145" textAnchor="middle" fill="#7B8FA1" className="font-mono text-xs">{label}</text>
      </svg>
      <span className="mt-3 inline-flex rounded-full border px-5 py-2 font-orbitron text-sm" style={{ borderColor: color, color, background: `${color}22` }}>{verdict}</span>
    </div>
  );
}

function IngredientCard({ item, index }) {
  const [open, setOpen] = useState(false);
  const status = item.status || (item.severity === "high" ? "avoid" : item.severity === "medium" ? "caution" : "safe");
  const color = status === "avoid" ? "danger" : status === "caution" ? "warning" : "mint";
  return (
    <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} onClick={() => setOpen(!open)} className={`glass clickable p-5 transition hover:-translate-y-1 ${status === "avoid" ? "shadow-danger" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <div><h3 className="font-bold text-ice">{item.name}</h3><p className="font-mono text-xs text-slate">{item.scientific_name || "Ingredient code unavailable"}</p></div>
        <span className={`rounded-full border px-3 py-1 font-mono text-xs uppercase ${color === "danger" ? "animate-pulse border-danger text-danger" : color === "warning" ? "border-warning text-warning" : "border-mint text-mint"}`}>{status === "avoid" ? "AVOID" : status}</span>
      </div>
      <motion.div initial={false} animate={{ height: open ? "auto" : 0, opacity: open ? 1 : 0 }} className="overflow-hidden">
        <p className="mt-4 text-sm leading-6 text-slate">{item.reason || "No specific issue identified by the AI rule engine."}</p>
        <div className="mt-4 rounded-2xl bg-white/5 p-4">
          <p className="text-sm font-semibold text-mint">Why this matters for you</p>
          <p className="mt-2 text-sm leading-6 text-slate">
            {item.why_this_matters || [item.personalized_warning, item.benefit, item.excess_warning].filter(Boolean).join(" ") || "No direct conflict with your saved profile was detected, but frequency and portion size still matter in the context of your whole diet."}
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}

function Nutriments({ nutriments = {} }) {
  const rows = [
    ["Carbs", nutriments.carbohydrates_100g ?? 0, "g", 65],
    ["Protein", nutriments.proteins_100g ?? 0, "g", 50],
    ["Fat", nutriments.fat_100g ?? 0, "g", 70],
    ["Sugar", nutriments.sugars_100g ?? 0, "g", 50],
    ["Sodium", Math.round((nutriments.sodium_100g ?? 0) * 1000), "mg", 2300],
    ["Fiber", nutriments.fiber_100g ?? 0, "g", 28]
  ];
  return (
    <GlassCard className="p-6">
      <h2 className="font-orbitron text-2xl font-bold">Nutriment Breakdown</h2>
      <div className="relative mt-6 space-y-4">
        <span className="absolute bottom-0 left-[72%] top-0 border-l border-dashed border-ice/30" />
        {rows.map(([name, value, unit, max], index) => {
          const pct = Math.min((value / max) * 100, 100);
          const color = pct > 70 ? "bg-danger" : pct > 45 ? "bg-warning" : "bg-mint";
          return (
            <div key={name} className="grid grid-cols-[70px_1fr_62px] items-center gap-2 sm:grid-cols-[90px_1fr_80px] sm:gap-3">
              <span className="text-sm text-slate">{name}</span>
              <div className="h-3 overflow-hidden rounded-full bg-white/10"><motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ delay: index * 0.1, duration: 0.8 }} className={`h-full ${color}`} /></div>
              <span className="font-mono text-xs text-ice">{value}{unit}</span>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
}

function HealthInsights({ analysis }) {
  const healthScore = analysis.health_score_out_of_10 ?? (typeof analysis.health_score === "number" ? Math.round(analysis.health_score) / 10 : null);
  const chips = [
    ["Healthy", analysis.is_healthy],
    ["Gym friendly", analysis.gym_friendly],
    ["Weight loss friendly", analysis.weight_loss_friendly]
  ];
  return (
    <GlassCard className="p-6">
      <h2 className="font-orbitron text-2xl font-bold">Health Insights</h2>
      <div className="mt-4 flex flex-wrap gap-2">
        {healthScore !== null && <span className="rounded-full border border-mint bg-mint/10 px-3 py-1 text-xs text-mint">Health score {healthScore}/10</span>}
        {chips.map(([label, active]) => <span key={label} className={`rounded-full border px-3 py-1 text-xs ${active ? "border-mint bg-mint/10 text-mint" : "border-warning bg-warning/10 text-warning"}`}>{active ? label : `Not ${label.toLowerCase()}`}</span>)}
      </div>
      <div className="mt-5 grid gap-4">
        <p className="text-sm leading-6 text-slate"><b className="text-ice">Sugar:</b> {analysis.sugar_analysis || "Sugar data was not available for this product."}</p>
        <p className="text-sm leading-6 text-slate"><b className="text-ice">Sodium:</b> {analysis.sodium_analysis || "Sodium data was not available for this product."}</p>
        <p className="text-sm leading-6 text-slate"><b className="text-ice">Fitness:</b> {analysis.fitness_analysis || "Fitness suitability depends on your goal, portion size, and total daily diet."}</p>
        <p className="text-sm leading-6 text-slate"><b className="text-ice">Daily use:</b> {analysis.daily_frequency_advice || "Use a normal portion and fit it into your daily nutrition goals."}</p>
        <p className="text-sm leading-6 text-slate"><b className="text-ice">Weekly use:</b> {analysis.weekly_frequency_advice || "Frequency depends on sugar, fat, sodium, and your overall diet."}</p>
      </div>
      {(analysis.harmful_ingredients?.length || analysis.preservatives?.length || analysis.artificial_colors_flavors?.length) && (
        <div className="mt-5 space-y-3 text-sm">
          {analysis.harmful_ingredients?.length > 0 && <p><span className="text-danger">Harmful ingredients:</span> {analysis.harmful_ingredients.join(", ")}</p>}
          {analysis.preservatives?.length > 0 && <p><span className="text-warning">Preservatives:</span> {analysis.preservatives.join(", ")}</p>}
          {analysis.artificial_colors_flavors?.length > 0 && <p><span className="text-warning">Artificial colors/flavors:</span> {analysis.artificial_colors_flavors.join(", ")}</p>}
        </div>
      )}
    </GlassCard>
  );
}

export default function Analysis() {
  const { productId } = useParams();
  const current = useScanStore((state) => state.currentAnalysis);
  const setCurrentAnalysis = useScanStore((state) => state.setCurrentAnalysis);
  const addScanToHistory = useScanStore((state) => state.addScanToHistory);
  const profile = useProfileStore();
  const toast = useUIStore((state) => state.toast);
  const [overlay, setOverlay] = useState(true);
  const [saved, setSaved] = useState(false);
  const [loadedAnalysis, setLoadedAnalysis] = useState(null);
  const [loadError, setLoadError] = useState("");
  const analysis = loadedAnalysis || current || fallback;
  const flags = analysis.flagged_ingredients || [];
  const topScore = analysis.health_score ?? analysis.safety_score ?? 0;

  useEffect(() => {
    let active = true;
    setOverlay(true);
    setLoadError("");
    setLoadedAnalysis(null);

    const currentMatchesRoute = current && (
      current.analysis_id === productId ||
      current.barcode === productId ||
      productId === "latest"
    );

    if (currentMatchesRoute) {
      setLoadedAnalysis(current);
      const timer = window.setTimeout(() => active && setOverlay(false), 700);
      return () => {
        active = false;
        window.clearTimeout(timer);
      };
    }

    analysisService.get(productId)
      .then((data) => {
        if (!active) return;
        setLoadedAnalysis(data);
        setCurrentAnalysis(data);
      })
      .catch(() => {
        if (!active) return;
        setLoadError("Could not load this analysis from the backend. Run a fresh scan or check the API server.");
        toast({ type: "error", title: "Analysis unavailable", message: "The saved report could not be loaded from the backend." });
      })
      .finally(() => {
        if (!active) return;
        window.setTimeout(() => active && setOverlay(false), 700);
      });

    const timer = window.setTimeout(() => setOverlay(false), 1500);
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [current, productId, setCurrentAnalysis, toast]);

  const save = () => {
    addScanToHistory({ ...analysis, created_at: new Date().toISOString() });
    setSaved(true);
    toast({ type: "success", title: "Saved to history", message: "Report archived locally." });
  };

  const share = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 900;
    canvas.height = 520;
    const ctx = canvas.getContext("2d");
    const shareScore = analysis.health_score ?? analysis.safety_score ?? 0;
    ctx.fillStyle = "#0A0F1E";
    ctx.fillRect(0, 0, 900, 520);
    ctx.fillStyle = scoreColor(shareScore);
    ctx.font = "bold 72px Orbitron";
    ctx.fillText(String(shareScore), 60, 130);
    ctx.fillStyle = "#E8F4FD";
    ctx.font = "bold 42px Orbitron";
    ctx.fillText(analysis.product_name || "PotionCheck Report", 60, 220);
    ctx.font = "24px Inter";
    ctx.fillText(`Verdict: ${analysis.verdict}`, 60, 270);
    ctx.fillText(`Top flags: ${flags.slice(0, 3).map((f) => f.name).join(", ") || "None"}`, 60, 320);
    const a = document.createElement("a");
    a.download = "potioncheck-report.png";
    a.href = canvas.toDataURL("image/png");
    a.click();
  };

  return (
    <PageTransition>
      {overlay && <motion.div exit={{ opacity: 0 }} className="fixed inset-0 z-50 grid place-items-center bg-space"><div className="text-center"><PotionIcon className="mx-auto h-20 w-20" /><DNASpinner className="mx-auto mt-5 h-20 w-20" /><p className="mt-5 font-mono text-mint">Analyzing ingredients with your health profile...</p></div></motion.div>}
      <motion.div variants={{ show: { transition: { staggerChildren: 0.15 } } }} initial="hidden" animate="show" className="mx-auto max-w-7xl space-y-8">
        <GlassCard className="grid gap-6 p-4 sm:p-6 md:grid-cols-[180px_1fr_260px] md:p-8">
          <div className="h-44 overflow-hidden rounded-3xl border border-mint/20 bg-ocean">{analysis.product_image_url ? <img src={analysis.product_image_url} alt={analysis.product_name} className="h-full w-full object-cover" /> : <div className="grid h-full place-items-center text-5xl">⚗</div>}</div>
          <div className="min-w-0"><h1 className="break-words font-orbitron text-2xl font-black leading-tight sm:text-3xl md:text-5xl">{analysis.product_name}</h1><p className="mt-2 break-words text-slate">{analysis.brand || analysis.brands}</p><p className="mt-3 break-all font-mono text-sm text-mint">{analysis.barcode}</p><div className="mt-4 flex flex-wrap gap-2">{(analysis.categories || []).slice?.(0, 5).map((tag) => <span key={tag} className="rounded-full bg-mint/10 px-3 py-1 text-xs text-mint">{tag}</span>)}</div></div>
          <SafetyMeter score={topScore} verdict={analysis.health_verdict?.toUpperCase?.() || analysis.verdict || "CAUTION"} />
        </GlassCard>
        {loadError && <div className="rounded-3xl border-l-4 border-warning bg-warning/10 p-5 text-warning">{loadError}</div>}
        {analysis.ollama_error && <div className="rounded-3xl border-l-4 border-warning bg-warning/10 p-5 text-warning">Ollama did not respond, so this report used local safety rules. Error: {analysis.ollama_error}</div>}
        {flags.length > 0 && <div className="rounded-3xl border-l-4 border-danger bg-danger/10 p-5 text-danger"><span className="inline-block animate-shake">⚠</span> {flags.length} ingredients flagged for your health profile</div>}
        <div className="grid gap-8 lg:grid-cols-[1fr_420px]">
          <section className="space-y-4">
            <h2 className="font-orbitron text-2xl font-bold">Ingredient Analysis</h2>
            {(analysis.all_ingredients?.length ? analysis.all_ingredients : flags).map((item, index) => <IngredientCard key={`${item.name}-${index}`} item={item} index={index} />)}
          </section>
          <div className="space-y-6">
            <Nutriments nutriments={analysis.nutriments} />
            <HealthInsights analysis={analysis} />
            <GlassCard className="p-6"><h2 className="font-orbitron text-2xl font-bold">Allergen Grid</h2><div className="mt-5 grid grid-cols-3 gap-3">{["Nut", "Milk", "Wheat", "Egg", "Soy", "Fish"].map((x, i) => <div key={x} className={`rounded-2xl p-4 text-center ${i < flags.length ? "bg-danger/20 text-danger animate-bounce" : "bg-white/5 text-slate"}`}>{x}</div>)}</div></GlassCard>
            <GlassCard className="p-6"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-full bg-mint/10 animate-pulse">AI</span><h2 className="font-orbitron text-xl font-bold">AI Verdict</h2></div><p className="mt-4 leading-7 text-slate">{analysis.ai_summary}</p><p className="mt-4 text-mint">{analysis.ai_recommendation}</p><p className="mt-3 text-sm text-slate">For someone with {profile.healthConditions.join(", ") || "no listed conditions"}, PotionCheck recommends reviewing the highlighted flags before frequent consumption.</p></GlassCard>
          </div>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Link to="/scanner" className="sm:w-auto"><GlowButton className="w-full rounded-2xl sm:w-auto">Scan Another Product</GlowButton></Link>
          <GlowButton onClick={save} variant="ghost">{saved ? "✓ Saved" : "Save to History"}</GlowButton>
          <GlowButton onClick={share} variant="ghost" className="w-full rounded-2xl sm:w-auto">Share Report</GlowButton>
        </div>
      </motion.div>
    </PageTransition>
  );
}

