/**
 * Utilitaires pour la gestion des fichiers
 */

/**
 * Normalise un nom de fichier pour éviter les problèmes de caractères spéciaux
 * et assurer la compatibilité avec les systèmes de fichiers
 *
 * @param filename - Nom de fichier original
 * @param addTimestamp - Si true, ajoute un timestamp pour assurer l'unicité
 * @returns Nom de fichier normalisé
 *
 * @example
 * normalizeFilename("Mon Fichier (2024).pdf") // "mon-fichier-2024.pdf"
 * normalizeFilename("Café & Thé.zip", true) // "cafe-et-the-20241206-143022.zip"
 */
export function normalizeFilename(
  filename: string,
  addTimestamp: boolean = false
): string {
  if (!filename) {
    filename = "unnamed-file";
  }

  // Séparer le nom et l'extension
  const lastDotIndex = filename.lastIndexOf(".");
  let name = lastDotIndex > 0 ? filename.substring(0, lastDotIndex) : filename;
  const ext = lastDotIndex > 0 ? filename.substring(lastDotIndex) : "";

  // Normaliser les caractères Unicode (enlever les accents)
  name = name.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  // Convertir en minuscules
  name = name.toLowerCase();

  // Remplacer les caractères spéciaux par des tirets
  // Garder seulement les lettres, chiffres, tirets et underscores
  name = name.replace(/[^a-z0-9\-_]/g, "-");

  // Remplacer les tirets multiples par un seul tiret
  name = name.replace(/-+/g, "-");

  // Supprimer les tirets en début et fin
  name = name.replace(/^-+|-+$/g, "");

  // Si le nom est vide après normalisation, utiliser un nom par défaut
  if (!name) {
    name = "file";
  }

  // Ajouter un timestamp si demandé
  if (addTimestamp) {
    const now = new Date();
    const timestamp = now
      .toISOString()
      .slice(0, 19)
      .replace(/[-\u003AT]/g, "")
      .replace(/(\d{8})(\d{6})/, "$1-$2");
    name = `${name}-${timestamp}`;
  }

  // Limiter la longueur du nom (max 100 caractères, plus 17 pour le timestamp si ajouté)
  const maxLength = addTimestamp ? 117 : 100;
  if (name.length > maxLength) {
    name = name.substring(0, maxLength).replace(/-+$/, "");
  }

  // Reconstituer le nom complet avec l'extension
  return `${name}${ext}`;
}

/**
 * Génère un nom de fichier unique avec timestamp
 *
 * @param filename - Nom de fichier original
 * @returns Nom de fichier unique avec timestamp
 */
export function generateUniqueFilename(filename: string): string {
  return normalizeFilename(filename, true);
}

/**
 * Construit un chemin de fichier avec préfixe de dossier
 *
 * @param folder - Nom du dossier (ex: "store_logos", "digital_products")
 * @param filename - Nom du fichier
 * @param addTimestamp - Si true, ajoute un timestamp
 * @returns Chemin complet du fichier
 */
export function buildFilePath(
  folder: string,
  filename: string,
  addTimestamp: boolean = true
): string {
  const normalizedFilename = normalizeFilename(filename, addTimestamp);
  return `${folder}/${normalizedFilename}`;
}
