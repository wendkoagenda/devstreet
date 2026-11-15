/** Accepte true / True / TRUE / 1 / yes (aligné sur USE_S3 Django et les .env). */
function envFlagTrue(value: unknown): boolean {
  const normalized = String(value ?? "")
    .trim()
    .toLowerCase();
  return normalized === "true" || normalized === "1" || normalized === "yes";
}

const config = {
  storage: {
    // Facultative : absente ou fausse = fichiers servis depuis /media/ (disque local).
    // true (backend avec USE_S3=True) = fichiers lus via /api/v1/files/, réservé aux utilisateurs connectés.
    use_s3: envFlagTrue(import.meta.env.VITE_USE_S3),
  },
};

export default config;
