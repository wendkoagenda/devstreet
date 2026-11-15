import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "./locales/en/common.json";
import fr from "./locales/fr/common.json";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      fr: { translation: fr },
    },
    // Produit FR d'abord : on n'impose pas la langue du navigateur.
    // Seul un choix explicite (localStorage) ou le fallback FR s'appliquent.
    fallbackLng: "fr",
    supportedLngs: ["fr", "en"],
    nonExplicitSupportedLngs: true,
    detection: {
      order: ["localStorage"],
      caches: ["localStorage"],
      lookupLocalStorage: "i18nextLng",
    },
    interpolation: {
      escapeValue: false,
    },
  });

function syncDocumentLang(lng: string) {
  if (typeof document === "undefined") return;
  document.documentElement.lang = lng.startsWith("en") ? "en" : "fr";
}

syncDocumentLang(i18n.language || "fr");
i18n.on("languageChanged", syncDocumentLang);

export default i18n;
