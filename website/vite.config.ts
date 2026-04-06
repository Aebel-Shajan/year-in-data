import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const DEV_WEB_URL = "https://pub-e4601d315b694fc3998db0702f6fabaf.r2.dev";

export default defineConfig(({ mode }) => {
  const isDev = mode === "development";
  const publicUrl = process.env.VITE_R2_PUBLIC_URL ?? (isDev ? DEV_WEB_URL : "");

  if (!publicUrl) throw new Error("VITE_R2_PUBLIC_URL is not set");

  return {
    plugins: [react()],
    base: "/year-in-data/",
    define: {
      __R2_PUBLIC_URL__: JSON.stringify(publicUrl),
    },
  };
});
