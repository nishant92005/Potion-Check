import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { GlowButton, GlassCard } from "../components/Interactive";
import { chatbotService } from "../services/chatbotService";
import { useScanStore, useUIStore } from "../stores/useStores";

function normalizeBackendProduct(product) {
  return { ...product, source: "backend", local_only: false };
}

function normalizeLocalProduct(item) {
  const scanId = item.scan_id || "";
  return {
    scan_id: scanId,
    analysis_id: item.analysis_id || null,
    barcode: item.barcode || "TEXT",
    product_name: item.product_name || "Unnamed product",
    product_image_url: item.product_image_url || "",
    safety_score: item.safety_score,
    verdict: item.verdict,
    flagged_count: item.flagged_count ?? item.flagged_ingredients?.length ?? 0,
    created_at: item.created_at || new Date().toISOString(),
    source: "local",
    local_only: !scanId
  };
}

function mergeProducts(backendProducts, localProducts) {
  const merged = new Map();
  backendProducts.forEach((product) => merged.set(product.scan_id || product.analysis_id, product));
  localProducts.forEach((product) => {
    const key = product.scan_id || product.analysis_id || product.barcode;
    if (!merged.has(key)) merged.set(key, product);
  });
  return Array.from(merged.values());
}

function ProductOption({ product, selected, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`grid w-full grid-cols-[56px_1fr_auto] items-center gap-3 rounded-2xl border p-3 text-left transition ${selected ? "border-mint bg-mint/10" : "border-white/10 bg-ocean/60 hover:border-mint/50"}`}
    >
      <div className="h-14 w-14 overflow-hidden rounded-2xl bg-space">
        {product.product_image_url ? <img src={product.product_image_url} alt="" className="h-full w-full object-cover" /> : <div className="grid h-full place-items-center font-orbitron text-mint">P</div>}
      </div>
      <div className="min-w-0">
        <p className="truncate font-semibold text-ice">{product.product_name || "Unnamed product"}</p>
        <p className="mt-1 truncate font-mono text-xs text-slate">{product.barcode || "TEXT"} · {new Date(product.created_at).toLocaleString()}</p>
      </div>
      <span className={`rounded-full border px-3 py-1 text-xs ${product.verdict === "SAFE" ? "border-mint text-mint" : product.verdict === "DANGER" ? "border-danger text-danger" : "border-warning text-warning"}`}>
        {product.safety_score}
      </span>
    </button>
  );
}

function Message({ message }) {
  const mine = message.role === "user";
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[88%] rounded-2xl border px-4 py-3 md:max-w-[72%] ${mine ? "border-mint/40 bg-mint/15 text-ice" : "border-white/10 bg-white/5 text-slate"}`}>
        <p className="whitespace-pre-wrap leading-7">{message.content}</p>
        {message.provider && <p className="mt-2 font-mono text-xs text-mint">via {message.provider} · {message.chunks || 0} chunks</p>}
      </div>
    </motion.div>
  );
}

export default function Chatbot() {
  const toast = useUIStore((state) => state.toast);
  const scanHistory = useScanStore((state) => state.scanHistory);
  const [products, setProducts] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [indexing, setIndexing] = useState(false);
  const [indexReady, setIndexReady] = useState(false);
  const [asking, setAsking] = useState(false);
  const [lastSources, setLastSources] = useState([]);
  const bottomRef = useRef(null);

  const localProducts = useMemo(() => scanHistory.map(normalizeLocalProduct), [scanHistory]);
  const selectedProduct = useMemo(() => products.find((item) => item.scan_id === selectedId), [products, selectedId]);

  useEffect(() => {
    let active = true;
    chatbotService.products()
      .then((data) => {
        if (!active) return;
        const backendProducts = (data.results || []).map(normalizeBackendProduct);
        const mergedProducts = mergeProducts(backendProducts, localProducts);
        setProducts(mergedProducts);
        setSelectedId(mergedProducts.find((product) => product.scan_id)?.scan_id || "");
      })
      .catch(() => {
        if (!active) return;
        setProducts(localProducts);
        setSelectedId(localProducts.find((product) => product.scan_id)?.scan_id || "");
        if (localProducts.length === 0) {
          toast({ type: "error", title: "Chatbot unavailable", message: "Scan a product first." });
        } else {
          toast({ type: "warning", title: "Using local history", message: "Backend product list was unavailable, so local history is shown." });
        }
      })
      .finally(() => active && setLoadingProducts(false));
    return () => {
      active = false;
    };
  }, [localProducts, toast]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, asking]);

  useEffect(() => {
    if (!selectedId) return;
    setMessages([]);
    setLastSources([]);
    setIndexReady(false);
    setIndexing(true);
    chatbotService.index(selectedId)
      .then((data) => {
        setIndexReady(true);
        toast({ type: "success", title: "Product ready", message: `${data.chunks} chunks stored in ChromaDB.` });
      })
      .catch(() => {
        toast({ type: "error", title: "Indexing failed", message: "Could not prepare this product for RAG chat." });
      })
      .finally(() => setIndexing(false));
  }, [selectedId, toast]);

  const ask = async (event) => {
    event.preventDefault();
    const text = question.trim();
    if (!selectedId || !text || asking) return;
    setQuestion("");
    setMessages((items) => [...items, { role: "user", content: text }]);
    setAsking(true);
    try {
      const data = await chatbotService.ask({ scan_id: selectedId, question: text });
      setLastSources(data.retrieved_chunks || []);
      setMessages((items) => [...items, { role: "assistant", content: data.answer, provider: data.provider, chunks: data.chunks }]);
    } catch (error) {
      const detail = error.response?.data?.detail || "The chatbot could not answer right now.";
      setMessages((items) => [...items, { role: "assistant", content: detail }]);
      toast({ type: "error", title: "Question failed", message: detail });
    } finally {
      setAsking(false);
    }
  };

  return (
    <PageTransition>
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[360px_1fr]">
        <section className="space-y-4">
          <div>
            <h1 className="font-orbitron text-3xl font-black md:text-4xl">Product Chatbot</h1>
            <p className="mt-3 max-w-2xl text-slate">Select one history item, then ask questions against that exact saved product snapshot.</p>
          </div>
          <GlassCard className="p-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="font-orbitron text-lg font-bold">History Products</h2>
              {indexing && <span className="rounded-full border border-mint px-3 py-1 font-mono text-xs text-mint">Indexing</span>}
            </div>
            <div className="mt-4 max-h-[560px] space-y-3 overflow-y-auto pr-1">
              {loadingProducts && <p className="rounded-2xl bg-white/5 p-4 text-slate">Loading saved products...</p>}
              {!loadingProducts && products.length === 0 && (
                <div className="rounded-2xl bg-white/5 p-4 text-slate">
                  <p>No saved backend history is available yet.</p>
                  <Link to="/scanner" className="mt-4 inline-flex text-mint">Scan a product</Link>
                </div>
              )}
              {products.map((product) => (
                <ProductOption key={product.scan_id || product.analysis_id || product.barcode} product={product} selected={product.scan_id === selectedId} onClick={() => product.scan_id && setSelectedId(product.scan_id)} />
              ))}
            </div>
          </GlassCard>
        </section>

        <section className="space-y-4">
          <GlassCard className="flex min-h-[640px] flex-col p-4 sm:p-6">
            <div className="border-b border-white/10 pb-4">
              <p className="font-orbitron text-xl font-bold">{selectedProduct?.product_name || "Select a product"}</p>
              <p className="mt-1 font-mono text-xs text-slate">
                {selectedProduct ? `${selectedProduct.verdict} · ${selectedProduct.flagged_count || 0} flags · ChromaDB RAG` : "Your answer will be grounded in selected history data."}
              </p>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto py-5">
              {messages.length === 0 && (
                <div className="grid min-h-[360px] place-items-center text-center">
                  <div>
                    <p className="font-orbitron text-2xl text-ice">Ask about ingredients, safety, nutrition, or frequency.</p>
                    <p className="mx-auto mt-3 max-w-xl text-slate">The question and saved product data are chunked, embedded, matched semantically in ChromaDB, then answered with Groq and Ollama fallback.</p>
                  </div>
                </div>
              )}
              {messages.map((message, index) => <Message key={`${message.role}-${index}`} message={message} />)}
              {asking && <Message message={{ role: "assistant", content: "Thinking over the retrieved chunks..." }} />}
              <div ref={bottomRef} />
            </div>

            <form onSubmit={ask} className="grid gap-3 border-t border-white/10 pt-4 sm:grid-cols-[1fr_auto]">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                disabled={!selectedId || asking || !indexReady}
                rows={2}
                className="focus-glow min-h-14 resize-none rounded-2xl border border-mint/20 bg-ocean/70 px-4 py-3 text-ice placeholder:text-slate"
                placeholder={selectedId ? (indexReady ? "Ask a question about this product..." : "Preparing this product for chat...") : "Select a backend-saved product first"}
              />
              <GlowButton type="submit" disabled={!selectedId || !question.trim() || asking || indexing || !indexReady} className="rounded-2xl px-6">
                Ask
              </GlowButton>
            </form>
          </GlassCard>

          {lastSources.length > 0 && (
            <GlassCard className="p-5">
              <h2 className="font-orbitron text-lg font-bold">Retrieved Sources</h2>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                {lastSources.slice(0, 4).map((source, index) => (
                  <div key={`${source.metadata?.chunk_index}-${index}`} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="font-mono text-xs text-mint">Chunk {source.metadata?.chunk_index + 1 || index + 1}</p>
                    <p className="mt-2 line-clamp-4 text-sm leading-6 text-slate">{source.text}</p>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}
        </section>
      </div>
    </PageTransition>
  );
}
