/**
 * Helper pour construire les URLs de fichiers média
 * Gère automatiquement le switch entre stockage local et GCS selon l'environnement
 */

import config from "@/config/config";
import { API_URL } from "@/helpers/api/csrf";

/**
 * Origine du backend, déduite de VITE_API_URL : celle de l'API si l'URL est absolue,
 * sinon celle de la page (le proxy ou le routeur relaie /media vers le backend).
 */
const backendOrigin = (): string => new URL(API_URL, window.location.origin).origin;

/**
 * Détermine si on est en environnement de production
 * @returns true si en production, false sinon
 */
function isProduction(): boolean {
  return (
    process.env.NODE_ENV === "production" ||
    process.env.NODE_ENV === "staging" ||
    (window.location.hostname !== "localhost" &&
      window.location.hostname !== "127.0.0.1")
  );
}

/**
 * Construit une URL complète pour un fichier média
 * @param filePath - Le chemin du fichier (ex: "store_logos/fichier.jpg" ou URL complète)
 * @returns L'URL complète du fichier
 */
export function buildMediaUrl(filePath: string): string {
  // Si c'est déjà une URL complète, la retourner telle quelle
  if (filePath.startsWith("http://") || filePath.startsWith("https://")) {
    return filePath;
  }

  // Si c'est un chemin absolu qui commence par /media/, le convertir vers le backend
  if (filePath.startsWith("/media/")) {
    const backendUrl = backendOrigin();
    return `${backendUrl}${filePath}`;
  }

  // Si c'est un autre chemin absolu, l'utiliser directement
  if (filePath.startsWith("/")) {
    return filePath;
  }

  // Si on est en production, construire une URL GCS
  if (isProduction()) {
    const gcsBucketName = config.gcs.bucket_name;
    // Sans bucket configuré (VITE_GCS_BUCKET_NAME absente), les fichiers sont servis par le backend
    if (gcsBucketName) {
      return `https://storage.googleapis.com/${gcsBucketName}/${filePath}`;
    }
  }

  // En développement, construire une URL locale vers le backend
  const backendUrl = backendOrigin();
  return `${backendUrl}/media/${filePath}`;
}

/**
 * Construit une URL GCS pour un fichier (force l'URL GCS même en local)
 * @param filePath - Le chemin du fichier
 * @returns L'URL GCS complète
 */
export function buildGcsUrl(filePath: string): string {
  const gcsBucketName = config.gcs.bucket_name;
  if (!gcsBucketName) {
    throw new Error(
      "VITE_GCS_BUCKET_NAME est requise pour construire une URL GCS (voir frontend/.env.example)."
    );
  }
  return `https://storage.googleapis.com/${gcsBucketName}/${filePath}`;
}

/**
 * Construit une URL locale pour un fichier (force l'URL locale même en production)
 * @param filePath - Le chemin du fichier
 * @returns L'URL locale complète
 */
export function buildLocalUrl(filePath: string): string {
  const backendUrl = backendOrigin();
  return `${backendUrl}/media/${filePath}`;
}

/**
 * Vérifie si une URL est une URL GCS
 * @param url - L'URL à vérifier
 * @returns true si c'est une URL GCS
 */
export function isGcsUrl(url: string): boolean {
  return (
    url.includes("storage.googleapis.com") ||
    url.includes("storage.cloud.google.com")
  );
}

/**
 * Vérifie si une URL est une URL locale
 * @param url - L'URL à vérifier
 * @returns true si c'est une URL locale
 */
export function isLocalUrl(url: string): boolean {
  return (
    url.startsWith("/media/") ||
    url.startsWith("http://localhost:8000") ||
    url.startsWith("http://127.0.0.1:8000") ||
    url.includes("/media/")
  );
}

/**
 * Extrait le chemin du fichier d'une URL (GCS ou locale)
 * @param url - L'URL complète
 * @returns Le chemin du fichier ou null si l'URL n'est pas valide
 */
export function extractFilePathFromUrl(url: string): string | null {
  if (isGcsUrl(url)) {
    // URL GCS illisible : pas de chemin extractible (contrat de la fonction)
    if (!URL.canParse(url)) return null;
    // Pour GCS: https://storage.googleapis.com/bucket/path/file.ext
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split("/");
    // Supprimer le premier élément vide et le nom du bucket
    return pathParts.slice(2).join("/");
  }
  if (isLocalUrl(url)) {
    // Pour local: /media/path/file.ext
    return url.replace("/media/", "");
  }
  return null;
}

/**
 * Convertit une URL GCS en URL locale (pour le développement)
 * @param gcsUrl - L'URL GCS
 * @returns L'URL locale équivalente
 */
export function gcsToLocalUrl(gcsUrl: string): string {
  const filePath = extractFilePathFromUrl(gcsUrl);
  return filePath ? buildLocalUrl(filePath) : gcsUrl;
}

/**
 * Convertit une URL locale en URL GCS (pour la production)
 * @param localUrl - L'URL locale
 * @returns L'URL GCS équivalente
 */
export function localToGcsUrl(localUrl: string): string {
  const filePath = extractFilePathFromUrl(localUrl);
  return filePath ? buildGcsUrl(filePath) : localUrl;
}

/**
 * Obtient l'URL appropriée selon l'environnement actuel
 * @param filePath - Le chemin du fichier ou URL existante
 * @returns L'URL appropriée selon l'environnement
 */
export function getAppropriateUrl(filePath: string): string {
  // Si c'est déjà une URL complète, la retourner telle quelle
  if (
    filePath.startsWith("http://") ||
    filePath.startsWith("https://") ||
    filePath.startsWith("/")
  ) {
    return filePath;
  }

  // Construire l'URL selon l'environnement
  return buildMediaUrl(filePath);
}
