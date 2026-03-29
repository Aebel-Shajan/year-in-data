import { readFileSync } from "fs";
import { resolve } from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

function readPublicUrl(file: string): string {
  const toml = readFileSync(resolve(__dirname, "../config", file), "utf-8");
  const match = toml.match(/public_url\s*=\s*"([^"]+)"/);
  if (!match) throw new Error(`Missing r2.public_url in ${file}`);
  return match[1];
}

export default defineConfig(({ mode }) => {
  const isDev = mode === "development";
  const publicUrl = process.env.VITE_R2_PUBLIC_URL ?? readPublicUrl(isDev ? "test.toml" : "config.toml");

  return {
    plugins: [react()],
    base: "/year-in-data/",
    define: {
      __R2_PUBLIC_URL__: JSON.stringify(publicUrl),
    },
  };
});
