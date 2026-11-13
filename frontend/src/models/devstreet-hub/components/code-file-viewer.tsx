import { ArrowLeft, Check, Copy, Download, FileCode2 } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { highlightLine } from "../functions/simple-highlight";
import type { CodeBlob } from "../schema";
import { copyText } from "@/helpers/clipboard";

interface CodeFileViewerProps {
  blob: CodeBlob;
  onBack: () => void;
}

function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

/** Lecteur de fichier : texte + numéros de ligne ; HTML jamais exécuté. */
export function CodeFileViewer({ blob, onBack }: CodeFileViewerProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const lines = useMemo(() => {
    if (!blob.content) return [];
    return blob.content.replace(/\r\n/g, "\n").split("\n");
  }, [blob.content]);

  const handleCopy = async () => {
    if (!blob.content) return;
    const ok = await copyText(blob.content);
    if (ok) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    }
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-border bg-card">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-muted/40 px-3 py-2">
        <div className="flex min-w-0 items-center gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-7 gap-1 px-2 text-xs"
            onClick={onBack}
          >
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.detail.code.back_tree")}
          </Button>
          <FileCode2 aria-hidden className="size-4 shrink-0 text-muted-foreground" />
          <span className="truncate font-mono text-xs font-semibold text-foreground">
            {blob.path}
          </span>
          <span className="hidden text-[11px] text-muted-foreground sm:inline">
            {blob.ref}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {blob.content ? (
            <>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 gap-1 text-xs"
                onClick={() => void handleCopy()}
              >
                {copied ? (
                  <Check aria-hidden className="size-3.5" />
                ) : (
                  <Copy aria-hidden className="size-3.5" />
                )}
                {copied ? t("hub.detail.code.copied") : t("hub.detail.code.copy")}
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 gap-1 text-xs"
                onClick={() => downloadText(blob.name, blob.content || "")}
              >
                <Download aria-hidden className="size-3.5" />
                {t("hub.detail.code.download")}
              </Button>
            </>
          ) : null}
        </div>
      </div>

      {blob.is_too_large ? (
        <p className="p-4 text-sm text-muted-foreground">
          {t("hub.detail.code.too_large")}
        </p>
      ) : blob.is_binary || !blob.content ? (
        <p className="p-4 text-sm text-muted-foreground">
          {t("hub.detail.code.binary")}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse font-mono text-xs leading-5">
            <tbody>
              {lines.map((line, index) => (
                <tr key={index} className="hover:bg-muted/30">
                  <td className="w-12 select-none border-r border-border bg-muted/20 px-2 py-0 text-right text-muted-foreground">
                    {index + 1}
                  </td>
                  <td className="whitespace-pre px-3 py-0 text-foreground">
                    {/* Texte React uniquement — HTML jamais exécuté. */}
                    {highlightLine(line || " ", blob.language)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {blob.language ? (
            <div className="border-t border-border px-3 py-1.5 text-[11px] text-muted-foreground">
              {t("hub.detail.code.language_label", { language: blob.language })}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
