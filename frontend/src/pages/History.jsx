import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { GlowButton, GlassCard } from "../components/Interactive";
import { useScanStore } from "../stores/useStores";

export default function History() {
  const history = useScanStore((state) => state.scanHistory);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const items = useMemo(() => history.filter((item) => (filter === "All" || item.verdict === filter.toUpperCase()) && (item.product_name || "").toLowerCase().includes(search.toLowerCase())), [filter, history, search]);
  return (
    <PageTransition>
      <div className="mx-auto max-w-6xl">
        <h1 className="font-orbitron text-3xl font-black md:text-4xl">Scan Timeline</h1>
        <div className="glass mt-7 flex flex-col gap-3 p-3 md:flex-row md:items-center">
          <div className="relative grid grid-cols-2 rounded-3xl bg-ocean/70 p-1 sm:flex sm:rounded-full">
            {["All", "Safe", "Caution", "Danger"].map((tab) => <button key={tab} onClick={() => setFilter(tab)} className={`relative min-h-11 rounded-full px-3 text-sm sm:px-5 ${filter === tab ? "text-space" : "text-slate"}`}>{filter === tab && <motion.span layoutId="history-filter" className="absolute inset-0 rounded-full bg-mint" />}<span className="relative">{tab}</span></button>)}
          </div>
          <input value={search} onChange={(e) => setSearch(e.target.value)} className="focus-glow flex-1 rounded-full border border-mint/20 bg-ocean/70 px-5 py-3" placeholder="Search by product name" />
        </div>
        {items.length === 0 ? (
          <div className="mt-20 text-center">
            <svg viewBox="0 0 300 180" className="mx-auto h-48 animate-float"><path d="M40 130h220" stroke="#00FFB2" strokeWidth="4" /><path d="M70 70h160v60H70z" fill="rgba(255,255,255,.03)" stroke="#00FFB2" /><circle cx="110" cy="100" r="18" fill="#7B61FF" opacity=".55" /><circle cx="180" cy="96" r="14" fill="#00FFB2" opacity=".55" /></svg>
            <p className="font-orbitron text-2xl">No scans yet. Start exploring your food.</p>
            <Link to="/scanner"><GlowButton className="mt-6">Start Scanning</GlowButton></Link>
          </div>
        ) : (
          <div className="relative mt-12">
            <span className="absolute left-4 top-0 h-full w-px bg-mint/40 md:left-1/2" />
            <div className="space-y-8">
              {items.map((item, index) => (
                <motion.div key={item.analysis_id || index} initial={{ opacity: 0, x: index % 2 ? 80 : -80 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className={`relative md:w-[48%] ${index % 2 ? "md:ml-auto" : ""}`}>
                  <span className="absolute -left-1 top-8 h-4 w-4 rounded-full bg-mint md:hidden" />
                  <Link to={`/analysis/${item.analysis_id || item.barcode || index}`}>
                    <GlassCard className="group p-5">
                      <div className="flex gap-4"><div className="h-20 w-20 shrink-0 rounded-2xl bg-ocean object-cover">{item.product_image_url && <img src={item.product_image_url} className="h-full w-full rounded-2xl object-cover" alt="" />}</div><div className="min-w-0"><h2 className="break-words font-bold">{item.product_name}</h2><p className="text-sm text-slate">{new Date(item.created_at).toLocaleString()}</p><span className="mt-2 inline-flex rounded-full border border-mint px-3 py-1 text-xs text-mint">{item.safety_score} score</span><p className="mt-2 text-sm text-slate">{item.flagged_ingredients?.length || item.flagged_count || 0} ingredients flagged</p></div></div>
                      <div className="mt-4 hidden flex-wrap gap-2 group-hover:flex">{(item.flagged_ingredients || []).slice(0, 3).map((flag) => <span key={flag.name} className="rounded-full bg-danger/15 px-3 py-1 text-xs text-danger">{flag.name}</span>)}</div>
                    </GlassCard>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageTransition>
  );
}
