const config = {
  storage: {
    // Facultative : absente ou différente de "true" = fichiers servis depuis /media/ (disque local).
    // "true" (backend avec USE_S3=True) = fichiers lus via /api/v1/files/, réservé aux utilisateurs connectés.
    use_s3: import.meta.env.VITE_USE_S3 === "true",
  },
};

export default config;
