import fs from "node:fs";
import path from "node:path";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const certPath = path.resolve("certs/dev-mobile.pfx");

  return {
    plugins: [react()],
    server: {
      port: 5173,
      https: fs.existsSync(certPath)
        ? {
            pfx: fs.readFileSync(certPath),
            passphrase: env.VITE_DEV_CERT_PASSPHRASE || "potioncheck-dev"
          }
        : undefined,
      proxy: {
        "/api": {
          target: env.VITE_PROXY_TARGET || "http://127.0.0.1:8001",
          changeOrigin: true
        }
      }
    }
  };
});
