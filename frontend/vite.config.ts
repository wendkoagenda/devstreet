import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    // Variables obligatoires du build, fournies explicitement aux tests (aucun repli dans le code)
    env: {
      VITE_API_URL: "http://localhost:8000/api",
      VITE_API_V1_URL: "http://localhost:8000/api/v1",
    },
    // Mesure de couverture (npm run test:coverage) : affichée par la CI, sans seuil pour l'instant
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/components/ui/**"],
      reporter: ["text-summary"],
    },
  },
  server: {
    // Le navigateur ne parle qu'au serveur Vite : /api est relayé vers Django, donc même origine
    // et cookies HttpOnly envoyés sans configuration CORS (voir 00readme/README_SAME_ORIGIN_COOKIES.md).
    proxy: {
      "/api": {
        // Serveur Django de développement (constante : outil de dev, pas une variable d'environnement)
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      // Fichiers téléversés (stockage local)
      "/media": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
