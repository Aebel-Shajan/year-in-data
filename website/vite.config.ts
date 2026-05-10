import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const DEV_WEB_URL =  "https://pub-043f9a3203b14d9ea123b68b96752245.r2.dev"//"http://localhost:9000/year-in-data-web";

export default defineConfig(({ mode }) => {
  const isDev = mode === "development";
  const publicUrl = process.env.VITE_R2_PUBLIC_URL ?? (isDev ? DEV_WEB_URL : "");

  if (!publicUrl) throw new Error("VITE_R2_PUBLIC_URL is not set");

  return {
    plugins: [react()],
    base: "/year-in-data/",
    server: { fs: { allow: [".."] } },
    define: {
      __R2_PUBLIC_URL__: JSON.stringify(publicUrl),
    },
  };
});
