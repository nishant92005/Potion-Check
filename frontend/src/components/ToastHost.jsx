import { AnimatePresence, motion } from "framer-motion";
import { useUIStore } from "../stores/useStores";

const styles = {
  success: ["border-mint", "✓"],
  error: ["border-danger", "×"],
  warning: ["border-warning", "!"],
  info: ["border-violet", "i"]
};

export function ToastHost() {
  const { toasts, dismissToast } = useUIStore();
  return (
    <div className="fixed right-4 top-24 z-50 flex w-[min(360px,calc(100vw-2rem))] flex-col gap-3">
      <AnimatePresence>
        {toasts.map((toast) => {
          const [border, icon] = styles[toast.type] || styles.info;
          return (
            <motion.button
              key={toast.id}
              type="button"
              onClick={() => dismissToast(toast.id)}
              initial={{ x: 420, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 420, opacity: 0 }}
              transition={{ type: "spring", stiffness: 260, damping: 24 }}
              className={`glass relative overflow-hidden border-l-4 ${border} p-4 text-left`}
            >
              <div className="flex gap-3">
                <span className="grid h-7 w-7 place-items-center rounded-full bg-white/10 font-mono text-mint">{icon}</span>
                <div>
                  <p className="font-semibold text-ice">{toast.title}</p>
                  {toast.message && <p className="mt-1 text-sm text-slate">{toast.message}</p>}
                </div>
              </div>
              <motion.span className="absolute bottom-0 left-0 h-0.5 bg-mint" initial={{ width: "100%" }} animate={{ width: 0 }} transition={{ duration: 4, ease: "linear" }} />
            </motion.button>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
