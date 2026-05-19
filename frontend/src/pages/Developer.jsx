import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { GlowButton, GlassCard } from "../components/Interactive";

export default function Developer() {
  return (
    <PageTransition>
      <section className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-8 px-1 py-10 sm:gap-10 sm:px-4 sm:py-16 md:grid-cols-[320px_1fr] md:py-20">
        <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.7 }} className="relative mx-auto w-full max-w-[240px] sm:max-w-[300px]">
          <div className="absolute -inset-4 rounded-[2.2rem] bg-[conic-gradient(from_90deg,#00FFB2,#FF9933,#7B61FF,#138808,#00FFB2)] opacity-35 blur-2xl" />
          <img src="/images/1.jpeg?v=20260519" alt="Nishant Sharma" className="relative aspect-square w-full rounded-[2rem] border border-mint/30 object-cover shadow-neon" />
        </motion.div>
        <GlassCard className="p-6 md:p-9">
          <motion.div initial={{ opacity: 0, y: 35 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <p className="font-mono text-sm uppercase tracking-[0.35em] text-mint">Developer Information</p>
            <h1 className="mt-4 break-words font-orbitron text-3xl font-black sm:text-4xl md:text-6xl">Nishant Sharma</h1>
            <p className="mt-5 text-base leading-7 text-slate md:text-lg">
              I am Nishant Sharma, a passionate AI enthusiast and tech creator who loves building smart and impactful projects. I enjoy exploring AI, Machine Learning, and modern technologies to solve real-world problems through creative ideas. From developing AI-powered web apps to experimenting with LLMs and computer vision, I am always curious to learn, innovate, and push my skills to the next level. Along with coding, I am also passionate about content creation, gaming, and technology-driven creativity.
            </p>
            <div className="mt-7 flex flex-wrap gap-2">
              {["AI", "Machine Learning", "LLMs", "Computer Vision", "Web Apps", "Gaming"].map((item) => <span key={item} className="rounded-full border border-mint/20 bg-mint/10 px-3 py-1 text-xs text-mint">{item}</span>)}
            </div>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <a href="https://github.com/nishant92005" target="_blank" rel="noreferrer"><GlowButton className="w-full rounded-2xl sm:w-auto">GitHub Profile</GlowButton></a>
              <a href="https://www.linkedin.com/in/nishant-sh4rma" target="_blank" rel="noreferrer"><GlowButton variant="ghost" className="w-full rounded-2xl sm:w-auto">LinkedIn Profile</GlowButton></a>
            </div>
          </motion.div>
        </GlassCard>
      </section>
    </PageTransition>
  );
}
