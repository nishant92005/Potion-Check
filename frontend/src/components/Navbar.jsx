import { AnimatePresence, motion } from "framer-motion";
import { Link, NavLink, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { PotionLogo } from "./PotionLogo";
import { useUserStore } from "../stores/useStores";

const links = [
  ["Home", "/"],
  ["Scanner", "/scanner"],
  ["History", "/history"],
  ["Chatbot", "/chatbot"],
  ["Profile", "/profile"],
  ["Developer", "/developer"],
  ["About", "/about"]
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const user = useUserStore((state) => state.user);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header className={`fixed inset-x-0 top-0 z-40 border-b transition-all duration-300 ${scrolled ? "border-mint/20 bg-space/80 shadow-neon backdrop-blur-2xl" : "border-white/5 bg-space/45 backdrop-blur-xl"}`}>
        <div className="h-0.5 bg-gradient-to-r from-mint to-violet" />
        <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 md:px-8">
          <Link to="/" className="clickable"><PotionLogo /></Link>
          <div className="hidden items-center gap-7 md:flex">
            {links.filter(([name]) => name !== "Profile").map(([name, path]) => {
              const active = location.pathname === path;
              return (
                <NavLink key={path} to={path} className="relative px-2 py-3 text-sm font-medium text-slate transition hover:text-ice">
                  {name}
                  {active && <motion.span layoutId="nav-dot" className="absolute -bottom-1 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-mint shadow-neon" />}
                </NavLink>
              );
            })}
          </div>
          <div className="hidden md:block">
            <Link to="/profile" className="grid h-11 min-w-11 place-items-center rounded-full border border-mint/40 bg-mint/10 px-4 font-semibold text-mint transition hover:bg-mint/20">
              {user?.full_name?.[0] || "Sign In"}
            </Link>
          </div>
          <button type="button" onClick={() => setOpen(true)} className="grid h-11 w-11 place-items-center rounded-full border border-mint/25 md:hidden">
            <span className="h-0.5 w-5 bg-mint shadow-[0_7px_0_#00FFB2,0_-7px_0_#00FFB2]" />
          </button>
        </nav>
      </header>
      <AnimatePresence>
        {open && (
          <motion.aside initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ type: "spring", stiffness: 240, damping: 28 }} className="fixed inset-0 z-50 bg-space/95 p-8 backdrop-blur-2xl md:hidden">
            <button className="ml-auto grid h-11 w-11 place-items-center rounded-full border border-mint/30 text-2xl text-mint" onClick={() => setOpen(false)}>×</button>
            <div className="mt-10 flex flex-col gap-5">
              {links.map(([name, path]) => (
                <Link key={path} to={path} onClick={() => setOpen(false)} className="glass px-5 py-4 font-orbitron text-xl text-ice">{name}</Link>
              ))}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
      <div className="fixed bottom-0 left-0 right-0 z-40 grid grid-cols-7 border-t border-mint/15 bg-space/90 px-1 pb-[calc(.5rem+env(safe-area-inset-bottom))] pt-2 backdrop-blur-xl md:hidden">
        {links.map(([name, path]) => (
          <Link key={path} to={path} className={`grid min-h-12 min-w-0 place-items-center gap-0.5 px-0.5 text-[10px] leading-tight ${location.pathname === path ? "text-mint" : "text-slate"}`}>
            <span className="font-orbitron">{name[0]}</span>
            <span className="w-full truncate px-0.5 text-center">{name === "Developer" ? "Dev" : name}</span>
          </Link>
        ))}
      </div>
    </>
  );
}
