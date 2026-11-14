import { useEffect, useMemo, useState } from "react";
import { X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useGetForumTagsQuery, useGetTagsSuivisQuery } from "../api";

type ComposerTagPickerProps = {
  value: string[];
  onChange: (labels: string[]) => void;
  max?: number;
};

/** Normalise une saisie libre (# ia, AI Infra…) vers un libellé stable. */
export function normalizeTagInput(raw: string): string {
  return raw
    .trim()
    .replace(/^#+/, "")
    .replace(/[\s_]+/g, " ")
    .trim();
}

function slugish(label: string): string {
  return normalizeTagInput(label)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function ComposerTagPicker({
  value,
  onChange,
  max = 3,
}: ComposerTagPickerProps) {
  const [draft, setDraft] = useState("");
  const [search, setSearch] = useState("");
  const { data: catalog = [] } = useGetForumTagsQuery({
    limit: 24,
    ...(search ? { search } : {}),
  });
  const { data: suivis = [] } = useGetTagsSuivisQuery();

  useEffect(() => {
    const q = normalizeTagInput(draft);
    if (q.length < 1) {
      setSearch("");
      return;
    }
    const handle = window.setTimeout(() => setSearch(q), 180);
    return () => window.clearTimeout(handle);
  }, [draft]);

  const selectedSlugs = useMemo(
    () => new Set(value.map((v) => slugish(v))),
    [value]
  );

  const suggestions = useMemo(() => {
    const fromSuivis = suivis.map((t) => ({ label: t.label, slug: t.slug }));
    const fromCatalog = catalog.map((t) => ({ label: t.label, slug: t.slug }));
    const merged = [...fromSuivis, ...fromCatalog].filter(
      (item, index, arr) =>
        arr.findIndex((x) => x.slug === item.slug) === index
    );
    const q = slugish(draft);
    const filtered = q
      ? merged.filter(
          (item) =>
            item.slug.includes(q) ||
            item.label.toLowerCase().includes(draft.trim().toLowerCase())
        )
      : merged;
    return filtered
      .filter((item) => !selectedSlugs.has(item.slug))
      .slice(0, 10);
  }, [catalog, draft, selectedSlugs, suivis]);

  const addLabel = (raw: string) => {
    const label = normalizeTagInput(raw);
    if (!label || value.length >= max) return;
    const key = slugish(label);
    if (!key || key.length < 2) return;
    // Réutilise le libellé catalogue si un slug correspond déjà.
    const known =
      suggestions.find((s) => s.slug === key) ||
      catalog.find((t) => t.slug === key) ||
      suivis.find((t) => t.slug === key);
    const finalLabel = known?.label ?? label;
    if (value.some((v) => slugish(v) === slugish(finalLabel))) return;
    onChange([...value, finalLabel]);
    setDraft("");
    setSearch("");
  };

  const removeAt = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-1.5">
        {value.map((label, index) => (
          <span
            key={`${slugish(label)}-${index}`}
            className="inline-flex items-center gap-1 rounded-md bg-brand-soft px-2 py-0.5 text-xs font-medium text-brand"
          >
            #{slugish(label) || label}
            <button
              type="button"
              aria-label={`Retirer ${label}`}
              className="rounded p-0.5 hover:bg-brand-soft-border/40"
              onClick={() => removeAt(index)}
            >
              <X className="size-3" aria-hidden />
            </button>
          </span>
        ))}
        {value.length < max ? (
          <Input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === ",") {
                event.preventDefault();
                if (suggestions[0] && slugish(draft).length >= 1) {
                  addLabel(suggestions[0].label);
                  return;
                }
                addLabel(draft);
              }
            }}
            placeholder="Thème (optionnel)"
            className="h-8 w-40 border-0 bg-muted/50 px-2 text-xs shadow-none focus-visible:ring-1"
            aria-autocomplete="list"
            aria-label="Ajouter un thème"
          />
        ) : null}
      </div>
      {suggestions.length > 0 && value.length < max ? (
        <div className="flex flex-wrap gap-1">
          {suggestions.map((item) => (
            <button
              key={item.slug}
              type="button"
              onClick={() => addLabel(item.label)}
              className={cn(
                "rounded-md border border-border px-2 py-0.5 font-mono text-[11px] text-muted-foreground",
                "transition-colors hover:border-brand-soft-border hover:bg-brand-soft hover:text-brand"
              )}
            >
              #{item.slug}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
