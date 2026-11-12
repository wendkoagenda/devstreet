import { languageColor } from "../functions/language-colors";

interface DetectedLanguage {
  name: string;
  percent?: number;
}

interface DetectedLanguageTagsProps {
  languages: DetectedLanguage[];
  emptyHint?: string;
}

/** Pastilles des langues détectées dans le dépôt (pas de sélection manuelle). */
export function DetectedLanguageTags({
  languages,
  emptyHint,
}: DetectedLanguageTagsProps) {
  if (languages.length === 0) {
    if (!emptyHint) return null;
    return <p className="text-xs text-muted-foreground">{emptyHint}</p>;
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {languages.map((lang) => (
        <span
          key={lang.name}
          className="inline-flex h-6 items-center gap-1.5 rounded border border-border bg-secondary px-2 text-[11px] text-secondary-foreground"
        >
          <span
            aria-hidden
            className="size-1.5 shrink-0 rounded-full"
            style={{ backgroundColor: languageColor(lang.name) }}
          />
          {lang.name}
          {lang.percent != null ? (
            <span className="text-muted-foreground">{lang.percent}%</span>
          ) : null}
        </span>
      ))}
    </div>
  );
}
