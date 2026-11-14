import { Download, FileText, FolderKanban } from "lucide-react";
import { Link } from "react-router-dom";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { looksLikeCodeBlock } from "../lib/parse-mixed-content";
import { parseRichMessage } from "../lib/rich-message";
import { ForumAudioPlayer } from "./forum-audio-player";
import { ForumRichText } from "./forum-rich-text";

type ChatMessageBodyProps = {
  texte: string;
  mine?: boolean;
  className?: string;
};

/**
 * Corps d'un message : texte, vocal, image, fichier ou carte projet Hub.
 */
export function ChatMessageBody({
  texte,
  mine = false,
  className,
}: ChatMessageBodyProps) {
  const parsed = parseRichMessage(texte);

  if (parsed.kind === "vocal") {
    return (
      <ForumAudioPlayer
        compact
        src={buildMediaUrl(parsed.url)}
        className={cn(
          mine ? "border-brand-foreground/20 bg-brand-foreground/10" : undefined,
          className
        )}
      />
    );
  }

  if (parsed.kind === "image") {
    return (
      <a
        href={buildMediaUrl(parsed.url)}
        target="_blank"
        rel="noreferrer"
        className={cn("block overflow-hidden rounded-xl", className)}
      >
        <img
          src={buildMediaUrl(parsed.url)}
          alt={parsed.name}
          className="max-h-64 max-w-full object-contain"
        />
      </a>
    );
  }

  if (parsed.kind === "file") {
    return (
      <a
        href={buildMediaUrl(parsed.url)}
        target="_blank"
        rel="noreferrer"
        download={parsed.name}
        className={cn(
          "flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition-colors",
          mine
            ? "border-brand-foreground/25 bg-brand-foreground/10 text-brand-foreground hover:bg-brand-foreground/15"
            : "border-border bg-card text-foreground hover:bg-muted",
          className
        )}
      >
        <FileText className="size-4 shrink-0" aria-hidden />
        <span className="min-w-0 flex-1 truncate font-medium">{parsed.name}</span>
        <Download className="size-3.5 shrink-0 opacity-70" aria-hidden />
      </a>
    );
  }

  if (parsed.kind === "project") {
    return (
      <Link
        to={`/hub/projects/${parsed.id}`}
        className={cn(
          "flex items-start gap-2.5 rounded-xl border px-3 py-2.5 text-left transition-colors",
          mine
            ? "border-brand-foreground/25 bg-brand-foreground/10 text-brand-foreground hover:bg-brand-foreground/15"
            : "border-border bg-card text-foreground hover:bg-muted",
          className
        )}
      >
        <span
          className={cn(
            "mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg",
            mine ? "bg-brand-foreground/15" : "bg-muted"
          )}
          aria-hidden
        >
          <FolderKanban className="size-4" />
        </span>
        <span className="min-w-0">
          <span className="block text-[10px] font-medium uppercase tracking-wide opacity-70">
            Projet Hub
          </span>
          <span className="block truncate text-sm font-semibold">
            {parsed.title}
          </span>
          <span className="mt-0.5 block text-xs opacity-80">
            Ouvrir dans le Hub →
          </span>
        </span>
      </Link>
    );
  }

  const hasCode = looksLikeCodeBlock(parsed.texte);
  return (
    <ForumRichText
      text={parsed.texte}
      compact
      className={cn(
        hasCode
          ? "text-foreground"
          : mine
            ? "text-brand-foreground [&_code]:border-brand-foreground/30 [&_code]:bg-brand-foreground/15 [&_code]:text-brand-foreground"
            : "text-foreground",
        className
      )}
    />
  );
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
