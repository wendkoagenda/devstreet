import type { ReactNode } from "react";

const KEYWORDS: Record<string, string[]> = {
  html: [],
  css: [
    "important",
    "from",
    "to",
    "and",
    "or",
    "not",
    "only",
  ],
  javascript: [
    "const",
    "let",
    "var",
    "function",
    "return",
    "if",
    "else",
    "for",
    "while",
    "class",
    "import",
    "export",
    "from",
    "async",
    "await",
    "new",
    "this",
    "typeof",
    "try",
    "catch",
    "throw",
    "null",
    "undefined",
    "true",
    "false",
  ],
  typescript: [
    "const",
    "let",
    "var",
    "function",
    "return",
    "if",
    "else",
    "for",
    "while",
    "class",
    "import",
    "export",
    "from",
    "async",
    "await",
    "new",
    "this",
    "typeof",
    "try",
    "catch",
    "throw",
    "null",
    "undefined",
    "true",
    "false",
    "interface",
    "type",
    "enum",
    "extends",
    "implements",
    "public",
    "private",
    "protected",
    "readonly",
  ],
  python: [
    "def",
    "class",
    "return",
    "if",
    "elif",
    "else",
    "for",
    "while",
    "import",
    "from",
    "as",
    "with",
    "try",
    "except",
    "raise",
    "True",
    "False",
    "None",
    "and",
    "or",
    "not",
    "in",
    "is",
    "lambda",
    "async",
    "await",
    "yield",
    "pass",
  ],
  json: ["true", "false", "null"],
};

function languageKey(language: string | null | undefined): string {
  const raw = (language || "").toLowerCase();
  if (raw.includes("html")) return "html";
  if (raw.includes("css")) return "css";
  if (raw.includes("typescript") || raw === "ts" || raw === "tsx") {
    return "typescript";
  }
  if (raw.includes("javascript") || raw === "js" || raw === "jsx") {
    return "javascript";
  }
  if (raw.includes("python") || raw === "py") return "python";
  if (raw.includes("json")) return "json";
  return raw || "text";
}

/**
 * Coloration légère sans dépendance externe.
 * Le contenu reste du texte React (jamais interprété comme HTML).
 */
export function highlightLine(
  line: string,
  language: string | null | undefined
): ReactNode[] {
  const key = languageKey(language);
  const keywords = new Set(KEYWORDS[key] ?? KEYWORDS.javascript ?? []);
  const isHtml = key === "html";
  const nodes: ReactNode[] = [];
  let i = 0;
  let tokenKey = 0;

  const push = (text: string, className?: string) => {
    if (!text) return;
    nodes.push(
      className ? (
        <span key={tokenKey++} className={className}>
          {text}
        </span>
      ) : (
        <span key={tokenKey++}>{text}</span>
      )
    );
  };

  while (i < line.length) {
    if (isHtml && line[i] === "<") {
      const end = line.indexOf(">", i);
      if (end === -1) {
        push(line.slice(i));
        break;
      }
      push(line.slice(i, end + 1), "text-brand");
      i = end + 1;
      continue;
    }

    if (line[i] === '"' || line[i] === "'" || line[i] === "`") {
      const quote = line[i];
      let j = i + 1;
      while (j < line.length) {
        if (line[j] === "\\" && j + 1 < line.length) {
          j += 2;
          continue;
        }
        if (line[j] === quote) {
          j += 1;
          break;
        }
        j += 1;
      }
      push(line.slice(i, j), "text-success");
      i = j;
      continue;
    }

    if (
      line[i] === "/" &&
      line[i + 1] === "/" &&
      key !== "python" &&
      key !== "html"
    ) {
      push(line.slice(i), "text-muted-foreground italic");
      break;
    }

    if (line[i] === "#" && key === "python") {
      push(line.slice(i), "text-muted-foreground italic");
      break;
    }

    if (/[A-Za-z_]/.test(line[i])) {
      let j = i + 1;
      while (j < line.length && /[A-Za-z0-9_]/.test(line[j])) j += 1;
      const word = line.slice(i, j);
      push(
        word,
        keywords.has(word) ? "text-info font-semibold" : undefined
      );
      i = j;
      continue;
    }

    if (/[0-9]/.test(line[i])) {
      let j = i + 1;
      while (j < line.length && /[0-9._]/.test(line[j])) j += 1;
      push(line.slice(i, j), "text-warning");
      i = j;
      continue;
    }

    push(line[i]);
    i += 1;
  }

  return nodes.length ? nodes : [" "];
}
