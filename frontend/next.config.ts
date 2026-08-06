import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Erzeugt ein eigenstaendiges Server-Bundle (.next/standalone) mit nur
  // den tatsaechlich benoetigten node_modules - deutlich kleineres
  // Docker-Image als ein vollstaendiges next start Setup.
  output: "standalone",
};

export default nextConfig;
