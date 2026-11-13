export type TextSegment = {
  type: "text";
  value: string;
};

export type CodeSegment = {
  type: "code";
  value: string;
  language?: string;
  inline?: boolean;
};

export type ContentSegment = TextSegment | CodeSegment;

const FENCE_RE = /```([a-zA-Z0-9_+-]*)\r?\n?([\s\S]*?)```/g;
const INLINE_CODE_RE = /`([^`\n]+)`/g;

const CODE_LINE_HINTS =
  /^(?:#{1,3}\s|\/\/|\/\*|\*\/|\*|import\s|from\s|export\s|const\s|let\s|var\s|function\s|def\s|class\s|return\s|raise\s|throw\s|pass\b|break\b|continue\b|yield\s|assert\s|with\s|if\s*\(|elif\s|else\s*:|for\s*\(|while\s*\(|switch\s*\(|case\s|try\s*:|catch\s*\(|except\s|finally\s*:|await\s|async\s|public\s|private\s|protected\s|using\s|package\s|self\.|this\.|<?php|<\/?[a-zA-Z]|@\w+|@staticmethod|@classmethod|@property)/;

const CODE_TOKEN_HINTS =
  /[{};=<>]|=>|::|\(|\)|\[|\]|\b(?:null|undefined|True|False|None|self|this|new|raise|throw)\b/;

function scoreCodeLine(line: string): number {
  const trimmed = line.trim();
  if (!trimmed) return 0;
  let score = 0;
  if (CODE_LINE_HINTS.test(trimmed)) score += 2;
  if (CODE_TOKEN_HINTS.test(trimmed)) score += 1;
  if (/[{};]$/.test(trimmed)) score += 1;
  if (/^\s{2,}|\t/.test(line)) score += 1;
  if (/^[a-zA-Z_][\w.]*\s*\(.*\)\s*\{?\s*$/.test(trimmed)) score += 1;
  // Appels / exceptions typiques : ValidationError(...), foo.bar(...)
  if (/^[A-Za-z_][\w.]*\s*\(.*\)\s*$/.test(trimmed)) score += 1;
  // Docstrings / chaînes multi-lignes Python
  if (/^("""|''')/.test(trimmed) || /("""|''')$/.test(trimmed)) score += 1;
  return score;
}

/** Heuristique : un bloc multi-lignes ressemble-t-il à du code ? */
export function looksLikeCodeBlock(text: string): boolean {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const nonEmpty = lines.filter((line) => line.trim().length > 0);
  if (nonEmpty.length < 2) return false;

  const scored = nonEmpty.filter((line) => scoreCodeLine(line) >= 2).length;
  const weak = nonEmpty.filter((line) => scoreCodeLine(line) >= 1).length;
  const ratio = scored / nonEmpty.length;
  const weakRatio = weak / nonEmpty.length;
  return (scored >= 2 && ratio >= 0.4) || (weak >= 3 && weakRatio >= 0.65);
}

function splitInlineCode(text: string): ContentSegment[] {
  const segments: ContentSegment[] = [];
  let lastIndex = 0;
  INLINE_CODE_RE.lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = INLINE_CODE_RE.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }
    segments.push({ type: "code", value: match[1], inline: true });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }

  return segments.length > 0 ? segments : [{ type: "text", value: text }];
}

function isClearProseLine(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed) return false;
  if (scoreCodeLine(line) >= 1) return false;
  // Phrase naturelle : commence par majuscule accentuée, peu de tokens code
  if (/^[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]/.test(trimmed) && /[.!?…]$/.test(trimmed)) {
    return trimmed.split(/\s+/).length >= 4;
  }
  return false;
}

function splitHeuristicCode(text: string): ContentSegment[] {
  const normalized = text.replace(/\r\n/g, "\n");
  if (!looksLikeCodeBlock(normalized)) {
    return splitInlineCode(normalized);
  }

  const lines = normalized.split("\n");
  const nonEmpty = lines.filter((line) => line.trim().length > 0);
  const strongCount = nonEmpty.filter((line) => scoreCodeLine(line) >= 2).length;
  const weakCount = nonEmpty.filter((line) => scoreCodeLine(line) >= 1).length;

  // Collage quasi entièrement code → un seul bloc (évite les coupures absurdes)
  if (
    strongCount / nonEmpty.length >= 0.45 ||
    weakCount / nonEmpty.length >= 0.75
  ) {
    const firstStrong = nonEmpty.findIndex((line) => scoreCodeLine(line) >= 2);
    const lastStrong =
      nonEmpty.length -
      1 -
      [...nonEmpty].reverse().findIndex((line) => scoreCodeLine(line) >= 1);

    // Préfixe / suffixe prose éventuel autour du collage
    if (firstStrong <= 0 && lastStrong >= nonEmpty.length - 1) {
      return [{ type: "code", value: normalized.trim() }];
    }
  }

  const segments: ContentSegment[] = [];
  let buffer: string[] = [];
  let bufferIsCode: boolean | null = null;

  const flush = () => {
    if (buffer.length === 0) return;
    const value = buffer.join("\n");
    if (bufferIsCode) {
      segments.push({ type: "code", value: value.replace(/^\n+|\n+$/g, "") });
    } else {
      segments.push(...splitInlineCode(value));
    }
    buffer = [];
    bufferIsCode = null;
  };

  for (const line of lines) {
    const empty = line.trim().length === 0;
    const score = empty ? 0 : scoreCodeLine(line);
    const indented = /^\s{2,}|\t/.test(line);

    let lineLooksCode: boolean;
    if (empty) {
      // Les lignes vides restent dans le mode courant
      lineLooksCode = bufferIsCode === true;
    } else if (bufferIsCode === true) {
      // Mode code « collant » : on ne sort que sur de la vraie prose
      lineLooksCode = score >= 1 || indented || !isClearProseLine(line);
    } else {
      lineLooksCode = score >= 2;
    }

    if (bufferIsCode === null) {
      bufferIsCode = lineLooksCode;
      buffer.push(line);
      continue;
    }

    if (lineLooksCode === bufferIsCode || (empty && bufferIsCode)) {
      buffer.push(line);
      continue;
    }

    flush();
    bufferIsCode = lineLooksCode;
    buffer.push(line);
  }
  flush();

  const codeParts = segments.filter((s) => s.type === "code" && !s.inline);
  if (codeParts.length === 0 && looksLikeCodeBlock(normalized)) {
    return [{ type: "code", value: normalized.trim() }];
  }

  // Trop fragmenté (ex. une ligne mal scorée au milieu) → tout fusionner en code
  if (codeParts.length >= 2) {
    const textParts = segments.filter(
      (s) => s.type === "text" && s.value.trim().length > 0
    );
    const onlyWeakGaps = textParts.every((s) => {
      const gapLines = s.value.split("\n").filter((l) => l.trim());
      return (
        gapLines.length <= 2 &&
        gapLines.every((l) => scoreCodeLine(l) >= 1 || !isClearProseLine(l))
      );
    });
    if (onlyWeakGaps) {
      return [{ type: "code", value: normalized.trim() }];
    }
  }

  return segments.filter(
    (segment) =>
      !(segment.type === "text" && segment.value.trim().length === 0) ||
      segment.value.includes("\n")
  );
}

/**
 * Découpe un texte forum en prose + blocs / extraits de code.
 * Priorité : fences markdown ``` → heuristique → inline `code`.
 */
export function parseMixedContent(raw: string): ContentSegment[] {
  const text = (raw ?? "").replace(/\r\n/g, "\n");
  if (!text.trim()) return [{ type: "text", value: text }];

  const segments: ContentSegment[] = [];
  let lastIndex = 0;
  FENCE_RE.lastIndex = 0;
  let match: RegExpExecArray | null;
  let sawFence = false;

  while ((match = FENCE_RE.exec(text)) !== null) {
    sawFence = true;
    if (match.index > lastIndex) {
      segments.push(...splitHeuristicCode(text.slice(lastIndex, match.index)));
    }
    const language = match[1]?.trim() || undefined;
    const code = match[2].replace(/^\n/, "").replace(/\n$/, "");
    segments.push({ type: "code", value: code, language });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    const rest = text.slice(lastIndex);
    segments.push(
      ...(sawFence ? splitInlineCode(rest) : splitHeuristicCode(rest))
    );
  }

  if (segments.length === 0) {
    return splitHeuristicCode(text);
  }

  return segments;
}
