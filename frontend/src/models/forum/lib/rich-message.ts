/**
 * Messages enrichis encodés dans le champ texte (même pattern que les vocaux).
 * Formats :
 * - [[vocal:url]]
 * - [[image:url|nom]]
 * - [[file:url|nom]]
 * - [[project:id|titre]]
 */

export type RichMessage =
  | { kind: "text"; texte: string }
  | { kind: "vocal"; url: string }
  | { kind: "image"; url: string; name: string }
  | { kind: "file"; url: string; name: string }
  | { kind: "project"; id: number; title: string };

const VOCAL_RE = /^\[\[vocal:([^\]]+)\]\]$/;
const IMAGE_RE = /^\[\[image:([^|\]]+)\|([^\]]+)\]\]$/;
const FILE_RE = /^\[\[file:([^|\]]+)\|([^\]]+)\]\]$/;
const PROJECT_RE = /^\[\[project:(\d+)\|([^\]]+)\]\]$/;

function sanitizeLabel(value: string) {
  return value.replace(/[[\]|]/g, " ").trim().slice(0, 120) || "fichier";
}

/** Extrait l'URL d'un message vocal encodé `[[vocal:…]]`. */
export function parseVocalUrl(texte: string): string | null {
  const match = (texte || "").trim().match(VOCAL_RE);
  return match?.[1] ?? null;
}

/** Encode une URL média en message vocal texte. */
export function encodeVocalMessage(url: string) {
  return `[[vocal:${url}]]`;
}

export function encodeImageMessage(url: string, name: string) {
  return `[[image:${url}|${sanitizeLabel(name)}]]`;
}

export function encodeFileMessage(url: string, name: string) {
  return `[[file:${url}|${sanitizeLabel(name)}]]`;
}

export function encodeProjectMessage(id: number, title: string) {
  return `[[project:${id}|${sanitizeLabel(title) || `Projet #${id}`}]]`;
}

/** Interprète le texte d'un message (texte libre ou payload enrichi). */
export function parseRichMessage(texte: string): RichMessage {
  const raw = (texte || "").trim();
  const vocal = raw.match(VOCAL_RE);
  if (vocal) return { kind: "vocal", url: vocal[1] };
  const image = raw.match(IMAGE_RE);
  if (image) return { kind: "image", url: image[1], name: image[2] };
  const file = raw.match(FILE_RE);
  if (file) return { kind: "file", url: file[1], name: file[2] };
  const project = raw.match(PROJECT_RE);
  if (project) {
    return {
      kind: "project",
      id: Number(project[1]),
      title: project[2],
    };
  }
  return { kind: "text", texte: texte || "" };
}

/** Indique si le message doit s'afficher en bulle « média » (pas de fond texte dense). */
export function isMediaBubble(texte: string) {
  const kind = parseRichMessage(texte).kind;
  return (
    kind === "vocal" ||
    kind === "image" ||
    kind === "file" ||
    kind === "project"
  );
}

/** Libellé court pour aperçus (réponse, liste…). */
export function richMessagePreview(texte: string) {
  const parsed = parseRichMessage(texte);
  switch (parsed.kind) {
    case "vocal":
      return "Message vocal";
    case "image":
      return `Image · ${parsed.name}`;
    case "file":
      return `Fichier · ${parsed.name}`;
    case "project":
      return `Projet · ${parsed.title}`;
    default:
      return parsed.texte;
  }
}
