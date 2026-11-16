import type { ReactNode } from "react";

/** Inline Markdown : texte React natif (échappé par React, jamais de HTML brut). */
function inline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const pattern =
    /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)|(\[[^\]]+\]\(https?:\/\/[^)\s]+\))/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index));
    }
    const token = match[0];
    if (token.startsWith("`")) {
      nodes.push(
        <code
          key={key++}
          className="rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith("**")) {
      nodes.push(<strong key={key++}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("*")) {
      nodes.push(<em key={key++}>{token.slice(1, -1)}</em>);
    } else {
      const link = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
      if (link) {
        nodes.push(
          <a
            key={key++}
            href={link[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-brand underline underline-offset-2"
          >
            {link[1]}
          </a>
        );
      }
    }
    last = match.index + token.length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

const isHeading = (line: string) => /^#{1,3}\s/.test(line);
const isFence = (line: string) => line.startsWith("```");
const isBullet = (line: string) => /^[-*]\s+/.test(line);
const isOrdered = (line: string) => /^\d+\.\s+/.test(line);
const isBlockStart = (line: string) =>
  isHeading(line) || isFence(line) || isBullet(line) || isOrdered(line);

/**
 * Rendu Markdown minimal et sûr : titres, listes, code, liens http(s).
 * Le HTML source est toujours échappé — jamais exécuté.
 */
export function SafeMarkdown({ content }: { content: string }) {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lines.length) {
    const line = lines[i];
    if (isFence(line)) {
      const lang = line.slice(3).trim();
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !isFence(lines[i])) {
        code.push(lines[i]);
        i += 1;
      }
      i += 1;
      blocks.push(
        <pre
          key={key++}
          className="overflow-x-auto whitespace-pre-wrap break-words rounded-lg border border-border bg-muted/60 p-3 font-mono text-xs leading-relaxed"
          data-language={lang || undefined}
        >
          <code className="whitespace-pre-wrap break-words">
            {code.join("\n")}
          </code>
        </pre>
      );
      continue;
    }
    if (isHeading(line)) {
      const level = line.match(/^#+/)?.[0].length ?? 1;
      const text = line.replace(/^#{1,3}\s/, "");
      const Tag = (`h${Math.min(level + 1, 4)}` as "h2" | "h3" | "h4");
      blocks.push(
        <Tag
          key={key++}
          className="mt-4 mb-2 font-semibold text-foreground first:mt-0"
        >
          {inline(text)}
        </Tag>
      );
      i += 1;
      continue;
    }
    if (isBullet(line)) {
      const items: string[] = [];
      while (i < lines.length && isBullet(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s+/, ""));
        i += 1;
      }
      blocks.push(
        <ul key={key++} className="mb-3 list-disc space-y-1 pl-5 text-sm">
          {items.map((item, index) => (
            <li key={index}>{inline(item)}</li>
          ))}
        </ul>
      );
      continue;
    }
    if (isOrdered(line)) {
      const items: string[] = [];
      while (i < lines.length && isOrdered(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s+/, ""));
        i += 1;
      }
      blocks.push(
        <ol key={key++} className="mb-3 list-decimal space-y-1 pl-5 text-sm">
          {items.map((item, index) => (
            <li key={index}>{inline(item)}</li>
          ))}
        </ol>
      );
      continue;
    }
    if (!line.trim()) {
      i += 1;
      continue;
    }
    const para: string[] = [];
    while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i])) {
      para.push(lines[i]);
      i += 1;
    }
    blocks.push(
      <p key={key++} className="mb-3 text-sm leading-relaxed text-foreground">
        {inline(para.join(" "))}
      </p>
    );
  }

  return <div className="safe-markdown max-w-none break-words">{blocks}</div>;
}
