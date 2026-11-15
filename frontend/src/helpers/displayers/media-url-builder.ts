/**
 * Helper pour construire les URLs de fichiers média
 * Deux modes, selon le backend :
 * - disque local : /media/<chemin> ;
 * - S3/MinIO (VITE_USE_S3=true) : /api/v1/files/<chemin>, servi par le backend à un utilisateur connecté (le bucket est privé).
 */

import config from "@/config/config";
import { API_URL } from "@/helpers/api/csrf";

const MEDIA_PREFIX = "/media/";
const FILES_PREFIX = "/api/v1/files/";

/**
 * Origine du backend, déduite de VITE_API_URL : celle de l'API si l'URL est absolue,
 * sinon celle de la page (le proxy ou le routeur relaie /media et /api vers le backend).
 */
const backendOrigin = (): string => new URL(API_URL, window.location.origin).origin;

/** Encode chaque segment du chemin (espaces, accents…) en gardant les « / ». */
const encodePath = (filePath: string): string =>
  filePath.split("/").map(encodeURIComponent).join("/");

/**
 * Si S3 est actif et que l'URL pointe vers /media/ sur l'origine backend,
 * renvoie l'équivalent /api/v1/files/… (forum/messagerie stockent souvent une URL absolue).
 */
const rewriteMediaPathForS3 = (pathname: string): string | null => {
  if (!config.storage.use_s3 || !pathname.startsWith(MEDIA_PREFIX)) {
    return null;
  }
  return buildFilesUrl(pathname.slice(MEDIA_PREFIX.length));
};

/**
 * Construit une URL complète pour un fichier média
 * @param filePath - Le chemin du fichier (ex: "store_logos/fichier.jpg" ou URL complète)
 * @returns L'URL complète du fichier
 */
export function buildMediaUrl(filePath: string): string {
  // URL absolue : réécrire https://…/media/… vers /api/v1/files/… si S3 (historique forum/chat)
  if (filePath.startsWith("http://") || filePath.startsWith("https://")) {
    try {
      const absolute = new URL(filePath);
      if (absolute.origin === backendOrigin()) {
        const rewritten = rewriteMediaPathForS3(absolute.pathname);
        if (rewritten) {
          return rewritten;
        }
      }
    } catch (error) {
      console.warn(`URL de média illisible, laissée telle quelle : ${filePath}`, error);
    }
    return filePath;
  }

  // Chemin /media/… avec S3 actif : le fichier est dans MinIO, pas sur le disque nginx.
  if (filePath.startsWith(MEDIA_PREFIX)) {
    const rewrittenRelative = rewriteMediaPathForS3(filePath);
    if (rewrittenRelative) {
      return rewrittenRelative;
    }
  }

  // Chemin absolu /media/… ou /api/v1/files/… : le convertir vers le backend
  if (filePath.startsWith(MEDIA_PREFIX) || filePath.startsWith(FILES_PREFIX)) {
    return `${backendOrigin()}${filePath}`;
  }

  // Si c'est un autre chemin absolu, l'utiliser directement
  if (filePath.startsWith("/")) {
    return filePath;
  }

  return config.storage.use_s3 ? buildFilesUrl(filePath) : buildLocalUrl(filePath);
}

/**
 * Construit l'URL de lecture authentifiée d'un fichier (stockage S3/MinIO)
 * @param filePath - Le chemin du fichier
 * @returns L'URL /api/v1/files/… complète
 */
export function buildFilesUrl(filePath: string): string {
  return `${backendOrigin()}${FILES_PREFIX}${encodePath(filePath)}`;
}

/**
 * Construit une URL locale pour un fichier (disque local)
 * @param filePath - Le chemin du fichier
 * @returns L'URL locale complète
 */
export function buildLocalUrl(filePath: string): string {
  return `${backendOrigin()}${MEDIA_PREFIX}${filePath}`;
}

/**
 * Vérifie si une URL est une URL de lecture authentifiée (/api/v1/files/…)
 * @param url - L'URL à vérifier
 */
export function isFilesUrl(url: string): boolean {
  return url.includes(FILES_PREFIX);
}

/**
 * Vérifie si une URL est une URL locale
 * @param url - L'URL à vérifier
 * @returns true si c'est une URL locale
 */
export function isLocalUrl(url: string): boolean {
  return (
    url.startsWith(MEDIA_PREFIX) ||
    url.startsWith("http://localhost:8000") ||
    url.startsWith("http://127.0.0.1:8000") ||
    url.includes(MEDIA_PREFIX)
  );
}

/**
 * Extrait le chemin du fichier d'une URL (/api/v1/files/… ou /media/…)
 * @param url - L'URL complète
 * @returns Le chemin du fichier ou null si l'URL n'est pas valide
 */
export function extractFilePathFromUrl(url: string): string | null {
  if (isFilesUrl(url)) {
    // Chemin tel qu'il apparaît dans l'URL (segments encodés), sans la requête ni le fragment
    const rest = url.slice(url.indexOf(FILES_PREFIX) + FILES_PREFIX.length);
    return rest.split(/[?#]/)[0];
  }
  if (isLocalUrl(url)) {
    // Pour local: /media/path/file.ext
    return url.replace(MEDIA_PREFIX, "");
  }
  return null;
}

/**
 * Obtient l'URL appropriée selon l'environnement actuel
 * @param filePath - Le chemin du fichier ou URL existante
 * @returns L'URL appropriée selon l'environnement
 */
export function getAppropriateUrl(filePath: string): string {
  return buildMediaUrl(filePath);
}
