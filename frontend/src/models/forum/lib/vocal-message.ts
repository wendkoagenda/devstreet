const VOCAL_RE = /^\[\[vocal:([^\]]+)\]\]$/;

/** Extrait l'URL d'un message vocal encodé `[[vocal:…]]`. */
export function parseVocalUrl(texte: string): string | null {
  const match = (texte || "").trim().match(VOCAL_RE);
  return match?.[1] ?? null;
}

/** Encode une URL média en message vocal texte. */
export function encodeVocalMessage(url: string) {
  return `[[vocal:${url}]]`;
}
