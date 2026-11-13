import { CheckCircle2, Star } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { CreateProjectFormState } from "../hooks/use-create-project";

interface CreateProjectPreviewProps {
  form: CreateProjectFormState;
  ownerLabel: string;
  ownerInitials: string;
  repoReady: boolean;
  defaultBranch: string;
}

export function CreateProjectPreview({
  form,
  ownerLabel,
  ownerInitials,
  repoReady,
  defaultBranch,
}: CreateProjectPreviewProps) {
  const { t } = useTranslation();
  const title = form.title.trim() || t("hub.create.preview.untitled");
  const initials =
    form.title
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || "PR";

  return (
    <aside
      aria-label={t("hub.create.preview.aside_label")}
      className="sticky top-24 flex flex-col gap-6 lg:col-span-4"
    >
      <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-card">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            {t("hub.create.preview.card_title")}
          </span>
          <span className="rounded bg-brand-soft px-2 py-0.5 text-[11px] font-semibold text-brand">
            {t("hub.create.preview.live")}
          </span>
        </div>

        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-sm font-bold text-primary-foreground">
            {initials}
          </div>
          <div className="flex min-w-0 flex-col">
            <h3 className="truncate text-sm font-bold text-foreground">{title}</h3>
            <span className="text-xs text-muted-foreground">
              {t("hub.create.preview.by", { owner: ownerLabel })}
            </span>
          </div>
        </div>

        <p className="line-clamp-3 text-xs leading-relaxed text-muted-foreground">
          {form.problem.trim() || t("hub.create.preview.problem_placeholder")}
        </p>

        <p className="text-[11px] leading-relaxed text-muted-foreground">
          {t("hub.create.preview.languages_auto")}
        </p>

        <div className="flex items-center justify-between border-t border-border pt-3 text-xs text-muted-foreground">
          <span>{form.declared_license}</span>
          <span className="inline-flex items-center gap-1">
            <Star aria-hidden className="size-3.5" />
            {t("hub.create.preview.stars", { count: 0 })}
          </span>
          {repoReady ? (
            <span className="inline-flex items-center gap-1 font-semibold text-success">
              <CheckCircle2 aria-hidden className="size-3.5" />
              {t("hub.create.preview.forge_sync")}
            </span>
          ) : null}
        </div>
      </div>

      <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-card">
        <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {t("hub.create.preview.params")}
        </h4>
        <dl className="flex flex-col gap-3 text-xs">
          <div className="flex items-center justify-between border-b border-border py-1.5">
            <dt className="text-muted-foreground">{t("hub.create.preview.owner")}</dt>
            <dd className="flex items-center gap-1.5 font-medium text-foreground">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                {ownerInitials}
              </span>
              {ownerLabel}
            </dd>
          </div>
          <div className="flex items-center justify-between border-b border-border py-1.5">
            <dt className="text-muted-foreground">{t("hub.create.preview.visibility")}</dt>
            <dd className="rounded bg-secondary px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
              {t("hub.create.preview.visibility_public")}
            </dd>
          </div>
          <div className="flex items-center justify-between border-b border-border py-1.5">
            <dt className="text-muted-foreground">{t("hub.create.preview.forge")}</dt>
            <dd className="flex items-center gap-1 text-[11px] font-medium text-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-brand" />
              {t("hub.create.preview.forge_name")}
            </dd>
          </div>
          <div className="flex items-center justify-between py-1.5">
            <dt className="text-muted-foreground">{t("hub.create.preview.branch")}</dt>
            <dd className="text-[11px] font-semibold text-foreground">{defaultBranch}</dd>
          </div>
        </dl>
      </div>

      <div className="flex flex-col gap-3 rounded-2xl border border-border bg-secondary/80 p-5">
        <div className="text-xs font-semibold text-foreground">
          {t("hub.create.preview.help_title")}
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          {t("hub.create.preview.help_text")}
        </p>
      </div>
    </aside>
  );
}
