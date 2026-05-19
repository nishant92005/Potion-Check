import { motion } from "framer-motion";

export function PageTransition({ children }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -30 }}
      transition={{ duration: 0.4, ease: "easeInOut" }}
      className="min-h-screen px-4 pb-[calc(6rem+env(safe-area-inset-bottom))] pt-24 sm:px-5 md:px-8 md:pb-24 md:pt-28"
    >
      {children}
    </motion.main>
  );
}
