import { profilePath } from "@/helpers/routes/profile-path";
import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { Check, Copy, Terminal } from "lucide-react";
import { copyText } from "@/helpers/clipboard";
import { cn } from "@/lib/utils";
import {
  parseMixedContent,
  type CodeSegment,
  type ContentSegment,
} from "../lib/parse-mixed-content";

type ForumRichTextProps = {
  text: string;
  className?: string;
  /** Style un peu plus compact (commentaires) */
  compact?: boolean;
};

const MENTION_RE = /(^|[\s([{'"])@([a-zA-Z0-9_.-]{2,32})\b/g;

function CodeBlock({
  segment,
  compact,
}: {
  segment: CodeSegment;
  compact?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const language = segment.language?.trim();

  const handleCopy = async () => {
    if (await copyText(segment.value)) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    }
  };

  if (segment.inline) {
    return (
      <code className="rounded-md border border-border bg-muted px-1.5 py-0.5 font-mono text-[0.85em] text-foreground">
        {segment.value}
      </code>
    );
  }

  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-border bg-muted/60 shadow-sm",
        compact ? "my-2" : "my-3"
      )}
    >
      <div className="flex items-center justify-between gap-2 border-b border-border bg-muted/80 px-3 py-1.5">
        <p className="inline-flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          <Terminal className="h-3.5 w-3.5" />
          {language || "Code"}
        </p>
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] text-muted-foreground transition-colors hover:bg-background hover:text-foreground"
          aria-label="Copier le code"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3" />
              Copié
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              Copier
            </>
          )}
        </button>
      </div>
      <pre
        className={cn(
          "overflow-x-auto p-3 font-mono text-[12.5px] leading-relaxed text-foreground",
          compact && "p-2.5 text-[12px]"
        )}
      >
        <code className="whitespace-pre">{segment.value}</code>
      </pre>
    </div>
  );
}

function renderTextWithMentions(value: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  MENTION_RE.lastIndex = 0;
  let match: RegExpExecArray | null;
  let part = 0;

  while ((match = MENTION_RE.exec(value)) !== null) {
    const prefix = match[1] ?? "";
    const username = match[2];
    const start = match.index;
    const mentionStart = start + prefix.length;
    if (mentionStart > lastIndex) {
      nodes.push(value.slice(lastIndex, mentionStart));
    }
    nodes.push(
      <Link
        key={`${keyPrefix}-m-${part++}`}
        to={profilePath(username)}
        className="font-medium text-brand hover:underline"
      >
        @{username}
      </Link>
    );
    lastIndex = mentionStart + 1 + username.length;
  }

  if (lastIndex < value.length) {
    nodes.push(value.slice(lastIndex));
  }

  return nodes.length > 0 ? nodes : [value];
}

function renderSegments(segments: ContentSegment[], compact?: boolean) {
  return segments.map((segment, index) => {
    if (segment.type === "code") {
      return (
        <CodeBlock
          key={`code-${index}`}
          segment={segment}
          compact={compact}
        />
      );
    }

    if (!segment.value) return null;

    return (
      <span key={`text-${index}`} className="whitespace-pre-wrap">
        {renderTextWithMentions(segment.value, `t${index}`)}
      </span>
    );
  });
}

export function ForumRichText({
  text,
  className,
  compact = false,
}: ForumRichTextProps) {
  const segments = parseMixedContent(text);
  const hasBlockCode = segments.some((s) => s.type === "code" && !s.inline);

  return (
    <div
      className={cn(
        "text-sm leading-relaxed text-muted-foreground",
        hasBlockCode && "space-y-1",
        className
      )}
    >
      {renderSegments(segments, compact)}
    </div>
  );
}
