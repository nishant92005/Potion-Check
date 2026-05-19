/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        space: "#0A0F1E",
        ocean: "#0D1B2A",
        mint: "#00FFB2",
        violet: "#7B61FF",
        danger: "#FF4560",
        warning: "#FFA500",
        ice: "#E8F4FD",
        slate: "#7B8FA1"
      },
      fontFamily: {
        orbitron: ["Orbitron", "sans-serif"],
        inter: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      },
      boxShadow: {
        neon: "0 0 22px rgba(0,255,178,0.7)",
        glass: "0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08)",
        danger: "0 0 22px rgba(255,69,96,0.35)"
      },
      keyframes: {
        universe: {
          "0%,100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" }
        },
        hexPulse: {
          "0%,100%": { opacity: "0.03" },
          "50%": { opacity: "0.07" }
        },
        drift: {
          "0%": { transform: "translateY(110vh)", opacity: "0" },
          "15%": { opacity: "0.2" },
          "100%": { transform: "translateY(-15vh)", opacity: "0" }
        },
        bubble: {
          "0%,100%": { transform: "translateY(0)", opacity: "0.65" },
          "50%": { transform: "translateY(-18px)", opacity: "1" }
        },
        liquid: {
          "0%,100%": { transform: "translateY(5px)" },
          "50%": { transform: "translateY(-5px)" }
        },
        heartbeat: {
          "0%,100%": { transform: "scale(1)", opacity: "1" },
          "35%": { transform: "scale(1.4)", opacity: "0.72" },
          "50%": { transform: "scale(0.95)", opacity: "1" }
        },
        pulseGlow: {
          "0%,100%": { boxShadow: "0 0 14px rgba(0,255,178,0.4)" },
          "50%": { boxShadow: "0 0 32px rgba(0,255,178,0.95)" }
        },
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" }
        },
        laser: {
          "0%": { transform: "translateY(0)" },
          "100%": { transform: "translateY(278px)" }
        },
        dash: {
          "100%": { strokeDashoffset: "-80" }
        },
        shake: {
          "0%,100%": { transform: "translateX(0)" },
          "20%,60%": { transform: "translateX(-7px)" },
          "40%,80%": { transform: "translateX(7px)" }
        },
        shimmer: {
          "0%": { backgroundPosition: "-700px 0" },
          "100%": { backgroundPosition: "700px 0" }
        }
      },
      animation: {
        universe: "universe 8s ease-in-out infinite",
        hexPulse: "hexPulse 6s ease-in-out infinite",
        drift: "drift linear infinite",
        bubble: "bubble 2.8s ease-in-out infinite",
        liquid: "liquid 3.2s ease-in-out infinite",
        heartbeat: "heartbeat 1.5s ease-in-out infinite",
        pulseGlow: "pulseGlow 2s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
        laser: "laser 2s ease-in-out infinite",
        dash: "dash 2s linear infinite",
        shake: "shake 0.35s ease-in-out",
        shimmer: "shimmer 1.7s linear infinite"
      }
    }
  },
  plugins: []
};
