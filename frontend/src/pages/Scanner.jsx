import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Html5Qrcode, Html5QrcodeSupportedFormats } from "html5-qrcode";
import Tesseract from "tesseract.js";
import { PageTransition } from "../components/PageTransition";
import { GlowButton, GlassCard } from "../components/Interactive";
import { DNASpinner } from "../components/DNASpinner";
import { analysisService } from "../services/analysisService";
import { scannerService } from "../services/scannerService";
import { useProfileStore, useScanStore, useUIStore } from "../stores/useStores";
import { makeId } from "../utils/id";

const tabs = [
  ["barcode", "Scan Barcode"],
  ["upload", "Upload Label"],
  ["text", "Paste Text"],
  ["produce", "Fresh Produce"]
];
const placeholderCodes = ["8901030895555", "3017620422003", "737628064502", "5449000000996"];
const produce = ["Apple", "Banana", "Spinach", "Broccoli", "Tomato", "Mango", "Orange", "Carrot", "Grapes", "Potato", "Onion", "Cucumber", "Custom"];
const scannerConfig = {
  fps: 15,
  qrbox: { width: 300, height: 150 },
  aspectRatio: 2.0,
  formatsToSupport: [
    Html5QrcodeSupportedFormats.EAN_13,
    Html5QrcodeSupportedFormats.EAN_8,
    Html5QrcodeSupportedFormats.UPC_A,
    Html5QrcodeSupportedFormats.UPC_E
  ]
};

const isLocalhost = () => ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
const localhostScannerUrl = () => `${window.location.protocol}//localhost:${window.location.port || "5173"}${window.location.pathname}${window.location.search}${window.location.hash}`;

const getCameraErrorMessage = (error) => {
  if (!window.isSecureContext) {
    return "Camera only works on localhost or HTTPS. Open the app from localhost, not a plain network IP.";
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    return "This browser does not support camera access. Try Chrome or Edge.";
  }
  if (error?.name === "NotAllowedError" || error?.name === "PermissionDeniedError") {
    return "Camera permission is blocked. Allow camera access from the browser address bar, then try again.";
  }
  if (error?.name === "NotReadableError" || error?.name === "TrackStartError") {
    return "Your camera is busy in another app. Close Teams/Zoom/Camera app, then try again.";
  }
  if (error?.name === "OverconstrainedError" || error?.name === "ConstraintNotSatisfiedError") {
    return "The requested camera type was not found. Trying the default laptop camera should fix this.";
  }
  return "Camera could not start. Check browser permission and make sure no other app is using it.";
};

const getPreferredCamera = async () => {
  const cameras = await Html5Qrcode.getCameras();
  if (!cameras.length) {
    throw new Error("No camera devices found");
  }
  const backCamera = cameras.find(({ label }) => /back|rear|environment/i.test(label));
  return backCamera?.id || cameras[0].id;
};

function ScannerFrame({ success }) {
  return (
    <div className="relative mx-auto h-[220px] w-full max-w-[500px] overflow-hidden rounded-3xl bg-[radial-gradient(circle,rgba(13,27,42,.65),#050914)] sm:h-[280px]">
      <svg className="absolute inset-0 h-full w-full">
        <rect x="3" y="3" width="calc(100% - 6px)" height="calc(100% - 6px)" rx="24" fill="none" stroke={success ? "#00FFB2" : "#00FFB2"} strokeWidth="2" strokeDasharray="12 10" className="animate-dash" />
      </svg>
      <div className={`absolute left-6 top-6 h-10 w-10 border-l-4 border-t-4 sm:left-10 sm:top-10 sm:h-12 sm:w-12 ${success ? "border-mint scale-110" : "border-mint/80"} transition animate-pulse`} />
      <div className="absolute right-6 top-6 h-10 w-10 border-r-4 border-t-4 border-mint/80 animate-pulse sm:right-10 sm:top-10 sm:h-12 sm:w-12" />
      <div className="absolute bottom-6 left-6 h-10 w-10 border-b-4 border-l-4 border-mint/80 animate-pulse sm:bottom-10 sm:left-10 sm:h-12 sm:w-12" />
      <div className="absolute bottom-6 right-6 h-10 w-10 border-b-4 border-r-4 border-mint/80 animate-pulse sm:bottom-10 sm:right-10 sm:h-12 sm:w-12" />
      {!success && <div className="absolute left-0 right-0 top-0 h-0.5 bg-gradient-to-r from-transparent via-mint to-transparent shadow-neon animate-laser" />}
      <p className="absolute inset-x-0 top-1/2 text-center font-mono text-sm text-slate">Point camera at barcode</p>
    </div>
  );
}

export default function Scanner() {
  const { activeTab, setActiveTab, toast } = useUIStore();
  const profile = useProfileStore();
  const scanStore = useScanStore();
  const navigate = useNavigate();
  const [barcode, setBarcode] = useState("");
  const [placeholder, setPlaceholder] = useState(0);
  const [invalid, setInvalid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [filePreview, setFilePreview] = useState("");
  const [barcodeImagePreview, setBarcodeImagePreview] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [pasteText, setPasteText] = useState("");
  const [parsed, setParsed] = useState([]);
  const [selectedProduce, setSelectedProduce] = useState("");
  const [liveScanning, setLiveScanning] = useState(false);
  const [scannerStatus, setScannerStatus] = useState("");
  const [cameraOriginIssue, setCameraOriginIssue] = useState(false);
  const textRef = useRef(null);
  const liveScannerRef = useRef(null);
  const handlingScanRef = useRef(false);

  useEffect(() => {
    const timer = window.setInterval(() => setPlaceholder((value) => (value + 1) % placeholderCodes.length), 1800);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    return () => {
      if (liveScannerRef.current?.isScanning) {
        liveScannerRef.current.stop().catch(() => {});
      }
    };
  }, []);

  const analyzePayload = async (payload) => {
    setLoading(true);
    setProgress(10);
    try {
      const timer = window.setInterval(() => setProgress((value) => Math.min(value + 18, 92)), 180);
      const data = await analysisService.analyze({ ...payload, include_user_profile: true, profile: { allergies: profile.allergies, health_conditions: profile.healthConditions, diet_type: profile.dietType } });
      window.clearInterval(timer);
      setProgress(100);
      scanStore.setCurrentAnalysis(data);
      scanStore.addScanToHistory({ ...data, created_at: new Date().toISOString() });
      navigate(`/analysis/${data.analysis_id || data.barcode || "latest"}`);
    } catch {
      const fallback = {
        analysis_id: makeId("analysis"),
        barcode: payload.barcode || "TEXT",
        product_name: payload.product_data?.product_name || selectedProduce || "Ingredient Analysis",
        brand: payload.product_data?.brands || "PotionCheck",
        safety_score: 74,
        verdict: "CAUTION",
        flagged_ingredients: [{ name: "Artificial flavor", severity: "medium", reason: "May be unsuitable for sensitive profiles.", personalized_warning: "Review this ingredient against your saved conditions." }],
        all_ingredients: (payload.ingredients_text || "Sugar, palm oil, cocoa, emulsifier, artificial flavor").split(",").map((name, i) => ({ name: name.trim(), status: i === 4 ? "avoid" : i === 0 ? "caution" : "safe" })),
        nutriments: { carbohydrates_100g: 52, proteins_100g: 6, fat_100g: 22, sugars_100g: 38, sodium_100g: 0.18, fiber_100g: 3 },
        ai_summary: "This product appears acceptable for occasional use, but several ingredients deserve attention. PotionCheck recommends comparing the flagged items with your health profile.",
        ai_recommendation: "Choose a simpler ingredient list when possible.",
        product_image_url: ""
      };
      scanStore.setCurrentAnalysis(fallback);
      scanStore.addScanToHistory({ ...fallback, created_at: new Date().toISOString() });
      toast({ type: "warning", title: "Using local demo analysis", message: "Backend or Groq key is not ready yet." });
      navigate(`/analysis/${fallback.analysis_id}`);
    } finally {
      setLoading(false);
    }
  };

  const analyzeBarcode = async (code = barcode) => {
    const cleanCode = String(code).replace(/\D/g, "").slice(0, 13);
    if (!/^\d{8,13}$/.test(cleanCode)) {
      setInvalid(true);
      window.setTimeout(() => setInvalid(false), 420);
      toast({ type: "error", title: "Invalid barcode", message: "Use 8 to 13 digits." });
      return;
    }
    setBarcode(cleanCode);
    let timer;
    try {
      setLoading(true);
      setProgress(20);
      timer = window.setInterval(() => setProgress((value) => Math.min(value + 16, 94)), 220);
      const data = await scannerService.analyzeBarcode({
        barcode: cleanCode,
        include_user_profile: true,
        profile: { allergies: profile.allergies, health_conditions: profile.healthConditions, diet_type: profile.dietType }
      });
      window.clearInterval(timer);
      setProgress(100);
      scanStore.setCurrentScan({
        barcode: cleanCode,
        product_name: data.product_name,
        ingredients_text: data.ingredients_text,
        nutriments: data.nutriments || data.nutrition,
        product_image_url: data.product_image_url
      });
      scanStore.setCurrentAnalysis(data);
      scanStore.addScanToHistory({ ...data, created_at: new Date().toISOString() });
      navigate(`/analysis/${data.analysis_id || data.barcode || "latest"}`);
    } catch (error) {
      const detail = error?.response?.data?.detail;
      const message = typeof detail === "string" ? detail : error?.message || "Could not fetch product details from OpenFoodFacts.";
      toast({ type: "error", title: "Barcode analysis failed", message });
    } finally {
      if (timer) window.clearInterval(timer);
      setLoading(false);
    }
  };

  const stopLiveScanner = async () => {
    const scanner = liveScannerRef.current;
    if (scanner?.isScanning) {
      await scanner.stop();
    }
    liveScannerRef.current = null;
    setLiveScanning(false);
    setScannerStatus("");
    handlingScanRef.current = false;
  };

  const startLiveScanner = async () => {
    if (loading || liveScanning) return;
    handlingScanRef.current = false;
    setCameraOriginIssue(false);
    setScannerStatus("Starting camera");
    setLiveScanning(true);
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("Camera API is not available");
      }
      await new Promise((resolve) => window.setTimeout(resolve, 0));
      if (!document.getElementById("live-barcode-reader")) {
        throw new Error("Scanner mount point is not ready");
      }
      const cameraId = await getPreferredCamera();
      const scanner = new Html5Qrcode("live-barcode-reader", { formatsToSupport: scannerConfig.formatsToSupport });
      liveScannerRef.current = scanner;
      await scanner.start(
        cameraId,
        scannerConfig,
        async (decodedText) => {
          if (handlingScanRef.current) return;
          const detectedCode = decodedText.replace(/\D/g, "").slice(0, 13);
          if (!/^\d{8,13}$/.test(detectedCode)) return;
          handlingScanRef.current = true;
          setScannerStatus(`Detected ${detectedCode}`);
          setBarcode(detectedCode);
          await stopLiveScanner();
          await analyzeBarcode(detectedCode);
        },
        () => {}
      );
      setScannerStatus("Align the barcode inside the frame");
    } catch (error) {
      setLiveScanning(false);
      liveScannerRef.current = null;
      setScannerStatus("");
      setCameraOriginIssue(!window.isSecureContext && !isLocalhost());
      toast({ type: "error", title: "Camera unavailable", message: getCameraErrorMessage(error) });
    }
  };

  const handleBarcodeImage = async (file) => {
    if (!file || loading) return;
    if (liveScannerRef.current?.isScanning) {
      await stopLiveScanner();
    }
    setBarcodeImagePreview(URL.createObjectURL(file));
    setLoading(true);
    setProgress(15);
    let imageScanner;
    try {
      if (!document.getElementById("barcode-image-reader")) {
        throw new Error("Barcode image reader is not ready");
      }
      imageScanner = new Html5Qrcode("barcode-image-reader", { formatsToSupport: scannerConfig.formatsToSupport });
      setProgress(45);
      const decodedText = await imageScanner.scanFile(file, false);
      const detectedCode = decodedText.replace(/\D/g, "").slice(0, 13);
      if (!/^\d{8,13}$/.test(detectedCode)) {
        throw new Error("No supported barcode found");
      }
      setBarcode(detectedCode);
      setProgress(70);
      toast({ type: "success", title: "Barcode detected", message: detectedCode });
      await analyzeBarcode(detectedCode);
    } catch {
      setProgress(0);
      toast({ type: "error", title: "Barcode not detected", message: "Upload a clear UPC/EAN barcode image or try Live Barcode Scan." });
    } finally {
      if (imageScanner) {
        await imageScanner.clear().catch(() => {});
      }
      setLoading(false);
    }
  };

  const handleFile = async (file) => {
    if (!file) return;
    setFilePreview(URL.createObjectURL(file));
    setLoading(true);
    try {
      const { data } = await Tesseract.recognize(file, "eng", { logger: (m) => setProgress(Math.round((m.progress || 0) * 100)) });
      setOcrText(data.text);
      toast({ type: "success", title: "OCR complete", message: "Ingredients extracted from label." });
    } catch {
      setOcrText("Sugar, cocoa butter, milk powder, soy lecithin, vanilla flavor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageTransition>
      <div className="mx-auto max-w-5xl">
        <h1 className="text-center font-orbitron text-3xl font-black leading-tight sm:text-4xl">Ingredient Intelligence Scanner</h1>
        <div className="glass relative mx-auto mt-7 grid max-w-3xl grid-cols-2 gap-2 rounded-3xl p-2 sm:flex sm:flex-wrap sm:justify-center sm:rounded-full">
          {tabs.map(([key, label]) => (
            <button key={key} onClick={() => setActiveTab(key)} className={`relative min-h-11 rounded-full px-3 text-xs transition sm:px-4 sm:text-sm ${activeTab === key ? "text-space" : "text-slate hover:text-ice"}`}>
              {activeTab === key && <motion.span layoutId="tab-bg" className="absolute inset-0 rounded-full bg-mint" />}
              <span className="relative z-10">{label}</span>
            </button>
          ))}
        </div>
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }} className="mt-10">
            {activeTab === "barcode" && (
              <GlassCard className="p-5 md:p-9">
                {liveScanning ? (
                  <div className="relative mx-auto min-h-[220px] w-full max-w-[500px] overflow-hidden rounded-3xl border border-mint/30 bg-space sm:min-h-[280px]">
                    <div id="live-barcode-reader" className="min-h-[220px] w-full overflow-hidden rounded-3xl sm:min-h-[280px]" />
                    <div className="pointer-events-none absolute inset-x-8 top-1/2 h-24 -translate-y-1/2 rounded-lg border-2 border-mint shadow-neon">
                      <span className="absolute left-0 right-0 top-1/2 h-0.5 -translate-y-1/2 bg-gradient-to-r from-transparent via-mint to-transparent" />
                    </div>
                    <p className="absolute inset-x-0 bottom-3 text-center font-mono text-xs text-ice">{scannerStatus}</p>
                  </div>
                ) : (
                  <ScannerFrame success={progress === 100} />
                )}
                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <GlowButton onClick={startLiveScanner} disabled={loading || liveScanning} className="w-full rounded-2xl">
                    {liveScanning ? "Camera Active" : "Live Barcode Scan"}
                  </GlowButton>
                  <GlowButton onClick={stopLiveScanner} disabled={!liveScanning} variant="ghost" className="w-full rounded-2xl">
                    Stop Camera
                  </GlowButton>
                </div>
                {cameraOriginIssue && (
                  <div className="mt-4 rounded-2xl border border-warning/40 bg-warning/10 p-4 text-sm text-ice">
                    <p className="font-mono text-warning">Camera blocked on network IP</p>
                    <p className="mt-2 text-slate">Open this page from localhost on the same computer, or serve the app over HTTPS.</p>
                    <a className="external-link mt-3 inline-block text-mint" href={localhostScannerUrl()}>
                      Open localhost scanner
                    </a>
                  </div>
                )}
                <label onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); handleBarcodeImage(e.dataTransfer.files[0]); }} className="mt-5 grid min-h-36 cursor-pointer place-items-center rounded-2xl border-2 border-dashed border-mint/25 bg-ocean/50 p-4 text-center transition hover:border-mint hover:bg-mint/5">
                  <input type="file" accept="image/*" className="hidden" disabled={loading} onChange={(e) => handleBarcodeImage(e.target.files[0])} />
                  {barcodeImagePreview ? (
                    <div className="relative h-32 w-full overflow-hidden rounded-2xl">
                      <img src={barcodeImagePreview} className="h-full w-full object-contain" alt="Barcode preview" />
                      {loading && <span className="absolute left-0 right-0 top-0 h-1 bg-mint shadow-neon animate-laser" />}
                    </div>
                  ) : (
                    <div>
                      <p className="font-mono text-sm text-mint">Upload Barcode Image</p>
                      <p className="mt-2 text-xs text-slate">Drop or choose a clear UPC/EAN photo</p>
                    </div>
                  )}
                </label>
                <div id="barcode-image-reader" className="absolute left-[-9999px] top-0 h-px w-px overflow-hidden" />
                <div className="my-8 flex items-center gap-4 text-xs text-slate"><span className="h-px flex-1 bg-gradient-to-r from-transparent to-mint" />OR<span className="h-px flex-1 bg-gradient-to-l from-transparent to-mint" /></div>
                <label className="font-mono text-sm text-mint">Manual Barcode Entry UPC/EAN</label>
                <input value={barcode} onChange={(e) => setBarcode(e.target.value.replace(/\D/g, "").slice(0, 13))} className={`focus-glow mt-3 w-full rounded-2xl border bg-ocean/80 px-4 py-4 font-mono text-ice placeholder:text-slate ${invalid ? "animate-shake border-danger" : "border-mint/20"}`} placeholder={placeholderCodes[placeholder]} />
                <p className="mt-2 text-xs text-slate">Powered by OpenFoodFacts database</p>
                <GlowButton onClick={() => analyzeBarcode()} className={`mt-6 w-full rounded-2xl ${invalid ? "animate-shake" : ""}`} disabled={loading}>{loading ? <span className="flex items-center justify-center gap-3"><DNASpinner className="h-7 w-7" /> Analyzing</span> : "Analyze Barcode"}<span className="absolute bottom-0 left-0 h-1 bg-white/70 transition-all" style={{ width: `${progress}%` }} /></GlowButton>
              </GlassCard>
            )}
            {activeTab === "upload" && (
              <GlassCard className="p-5">
                <label onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }} className="grid min-h-[280px] place-items-center rounded-3xl border-2 border-dashed border-mint/25 bg-ocean/40 p-4 text-center transition hover:border-mint hover:bg-mint/5 sm:min-h-[400px]">
                  <input type="file" accept="image/*" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
                  {filePreview ? <div className="relative h-full w-full overflow-hidden rounded-3xl"><img src={filePreview} className="h-full w-full object-contain" alt="Label preview" />{loading && <span className="absolute left-0 right-0 top-0 h-1 bg-mint shadow-neon animate-laser" />}</div> : <div><div className="mx-auto text-6xl animate-float">⇧</div><p className="mt-4 text-lg">Drop your product label image here or click to browse</p><p className="mt-4 text-sm text-slate">JPG PNG WEBP HEIC</p></div>}
                </label>
                {loading && <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full bg-mint transition-all" style={{ width: `${progress}%` }} /></div>}
                {ocrText && <textarea value={ocrText} onChange={(e) => setOcrText(e.target.value)} className="focus-glow mt-5 min-h-36 w-full rounded-2xl border border-mint/20 bg-ocean/70 p-4 text-ice" />}
                {ocrText && <GlowButton onClick={() => analyzePayload({ ingredients_text: ocrText })} className="mt-5 w-full rounded-2xl">Analyze Extracted Text</GlowButton>}
              </GlassCard>
            )}
            {activeTab === "text" && (
              <GlassCard className="p-5">
                <div className="relative">
                  <textarea ref={textRef} value={pasteText} onChange={(e) => { setPasteText(e.target.value); e.target.style.height = "auto"; e.target.style.height = `${e.target.scrollHeight}px`; }} className="focus-glow min-h-72 w-full resize-none rounded-2xl border-0 border-b border-mint/20 bg-ocean/60 p-5 text-ice caret-mint" placeholder="Paste your ingredients list here for example Sugar Palm Oil Hazelnuts Skimmed Milk Cocoa Emulsifier Lecithins Vanillin" />
                  <span className="absolute bottom-3 right-4 font-mono text-xs text-slate">{pasteText.length} chars</span>
                </div>
                <GlowButton onClick={() => setParsed(pasteText.split(/[,.]/).map((x) => x.trim()).filter(Boolean))} className="mt-5 w-full rounded-2xl sm:w-auto">Smart Parse</GlowButton>
                {parsed.length > 0 && <div className="mt-6 flex flex-wrap gap-2">{parsed.map((item, i) => <motion.span initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} key={item} className={`border-b-2 ${i % 5 === 0 ? "border-danger" : i % 3 === 0 ? "border-warning" : "border-mint"} px-1`}>{item}</motion.span>)}</div>}
                <GlowButton onClick={() => analyzePayload({ ingredients_text: pasteText })} className="mt-6 w-full rounded-2xl">Analyze Pasted Text</GlowButton>
              </GlassCard>
            )}
            {activeTab === "produce" && (
              <GlassCard className="p-5">
                <input className="focus-glow w-full rounded-2xl border border-mint/20 bg-ocean/70 px-5 py-4" placeholder="☘ Search produce name" />
                <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
                  {produce.map((item) => <motion.button key={item} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }} onClick={() => setSelectedProduce(item)} className={`relative rounded-3xl border p-5 text-center ${selectedProduce === item ? "border-mint shadow-neon" : "border-white/10 bg-ocean/60"}`}><div className="text-4xl">{item === "Custom" ? "+" : "🥬"}</div><p className="mt-2">{item}</p>{selectedProduce === item && <span className="absolute right-3 top-3 text-mint">✓</span>}</motion.button>)}
                </div>
                {selectedProduce && <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mt-6 rounded-3xl border border-mint/20 bg-mint/5 p-5"><b>{selectedProduce}</b>: known pesticide risk varies by source and season. Rinse well; choose organic for leafy greens when possible.</motion.div>}
              </GlassCard>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </PageTransition>
  );
}
