import { useEffect, useRef, useState } from "react";
import { makeId } from "../utils/id";

export function CustomCursor() {
  const dotRef = useRef(null);
  const ringRef = useRef(null);
  const target = useRef({ x: 0, y: 0 });
  const ring = useRef({ x: 0, y: 0 });
  const [enabled, setEnabled] = useState(false);
  const [hovering, setHovering] = useState(false);
  const [bursts, setBursts] = useState([]);

  useEffect(() => {
    const query = window.matchMedia("(pointer: fine) and (min-width: 768px)");
    const update = () => setEnabled(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (!enabled) return;
    const move = (event) => {
      target.current = { x: event.clientX, y: event.clientY };
      if (dotRef.current) dotRef.current.style.transform = `translate(${event.clientX - 4}px, ${event.clientY - 4}px)`;
      setHovering(Boolean(event.target.closest("button,a,input,textarea,[role='button'],.clickable")));
    };
    const click = (event) => {
      const id = makeId("burst");
      setBursts((items) => [...items, { id, x: event.clientX, y: event.clientY }]);
      window.setTimeout(() => setBursts((items) => items.filter((item) => item.id !== id)), 420);
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mousedown", click);
    let frame;
    const animate = () => {
      ring.current.x += (target.current.x - ring.current.x) * 0.18;
      ring.current.y += (target.current.y - ring.current.y) * 0.18;
      if (ringRef.current) ringRef.current.style.transform = `translate(${ring.current.x - 16}px, ${ring.current.y - 16}px) scale(${hovering ? 1.5 : 1})`;
      frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mousedown", click);
      cancelAnimationFrame(frame);
    };
  }, [enabled, hovering]);

  if (!enabled) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-[100] hidden md:block">
      <div ref={dotRef} className={`fixed h-2 w-2 rounded-full bg-mint transition-opacity ${hovering ? "opacity-0" : "opacity-100"}`} />
      <div ref={ringRef} className={`fixed h-8 w-8 rounded-full border border-mint transition-colors ${hovering ? "bg-mint/15" : "bg-transparent"}`} />
      {bursts.map((burst) => (
        <div key={burst.id} className="fixed" style={{ left: burst.x, top: burst.y }}>
          {Array.from({ length: 6 }).map((_, index) => (
            <span
              key={index}
              className="absolute h-1.5 w-1.5 rounded-full bg-mint"
              style={{
                animation: "burst 400ms ease-out forwards",
                transform: `rotate(${index * 60}deg) translateX(0)`
              }}
            />
          ))}
        </div>
      ))}
      <style>{`@keyframes burst{to{opacity:0;transform:rotate(var(--r,0deg)) translateX(28px)}}`}</style>
    </div>
  );
}
