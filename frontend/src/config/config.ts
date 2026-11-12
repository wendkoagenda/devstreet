const config = {
  gcs: {
    // Facultative : absente = pas de stockage GCS (fichiers servis par le backend).
    // L'absence est gérée explicitement par media-url-builder, sans valeur de repli.
    bucket_name: import.meta.env.VITE_GCS_BUCKET_NAME as string | undefined,
  },
};

export default config;
