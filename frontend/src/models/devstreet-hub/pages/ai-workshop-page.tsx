import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AlertTriangle,
  ArrowLeft,
  Check,
  ExternalLink,
  Loader2,
  Sparkles,
  Wand2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useAiWorkshop } from "../hooks/use-ai-workshop";

export default function AiWorkshopPage() {
  const { t } = useTranslation();
  const params = useParams();
  const projectId = Number(params.id);
  const workshop = useAiWorkshop(projectId);

  const hasResults = Boolean(
    workshop.analysis &&
      (workshop.analysis.status === "succeeded" ||
        workshop.analysis.status === "failed")
  );

  const selected = useMemo(() => {
    const list = workshop.suggestions;
    if (!list.length) return null;
    const index = Math.min(
      Math.max(workshop.selectedSuggestion, 0),
      list.length - 1
    );
    return { index, item: list[index] };
  }, [workshop.selectedSuggestion, workshop.suggestions]);

  if (!Number.isFinite(projectId) || projectId <= 0) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center text-sm text-muted-foreground">
        {t("hub.ai.errors.not_found")}
      </div>
    );
  }

  if (workshop.isLoading && !workshop.project) {
    return (
      <div className="mx-auto max-w-3xl py-16 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </div>
    );
  }

  if (workshop.isError || !workshop.project) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">
          {workshop.errorStatus === 403
            ? t("hub.ai.errors.forbidden")
            : t("hub.ai.errors.not_found")}
        </p>
        <Button asChild size="sm" variant="outline">
          <Link to="/hub/projects">
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.upcoming.back")}
          </Link>
        </Button>
      </div>
    );
  }

  const project = workshop.project;
  const result = workshop.result;
  const showResults = workshop.view === "results" && hasResults;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-4">
      <header className="sticky top-0 z-10 -mx-1 border-b border-border bg-background/95 px-1 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            <Button asChild size="sm" variant="ghost" className="px-2">
              <Link to={`/hub/projects/${project.id}`}>
                <ArrowLeft aria-hidden className="size-3.5" />
                {t("hub.ai.back_project")}
              </Link>
            </Button>
            <h1 className="flex items-center gap-1.5 text-base font-semibold text-foreground">
              <Sparkles aria-hidden className="size-4 text-brand" />
              {t("hub.ai.title")}
            </h1>
            {workshop.analysis ? (
              <span className="rounded-md border border-border bg-secondary/70 px-2 py-0.5 text-[11px] text-muted-foreground">
                #{workshop.analysis.id} · {workshop.progressLabel}
              </span>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {hasResults ? (
              <>
                <Button
                  type="button"
                  size="sm"
                  variant={showResults ? "outline" : "ghost"}
                  onClick={() => workshop.setView("compose")}
                >
                  {t("hub.ai.nav.compose")}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={showResults ? "default" : "outline"}
                  onClick={() => workshop.setView("results")}
                >
                  {t("hub.ai.nav.results")}
                  {workshop.suggestions.length
                    ? ` (${workshop.suggestions.length})`
                    : ""}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  onClick={workshop.clearResults}
                >
                  {t("hub.ai.nav.new_analysis")}
                </Button>
              </>
            ) : null}
            <Button asChild size="sm" variant="outline">
              <Link to={`/hub/projects/${project.id}?tab=contribute`}>
                {t("hub.ai.nav.project_tasks")}
                <ExternalLink aria-hidden className="size-3.5" />
              </Link>
            </Button>
          </div>
        </div>
      </header>

      {!showResults ? (
        <>
          <p className="max-w-3xl text-sm text-muted-foreground">
            {t("hub.ai.description")}
          </p>

          <section className="rounded-md border border-border bg-card p-4">
            <h2 className="mb-1.5 text-sm font-semibold text-foreground">
              {t("hub.ai.form.title")}
            </h2>
            <p className="mb-3 text-xs leading-relaxed text-muted-foreground">
              {t("hub.ai.consent.text")}
            </p>
            <div className="mb-3 flex flex-wrap items-center gap-1.5">
              <span className="rounded-md border border-border bg-secondary/60 px-2 py-0.5 text-[11px] text-muted-foreground">
                {workshop.hasConsent
                  ? t("hub.ai.consent.enabled")
                  : t("hub.ai.consent.disabled")}
              </span>
              {workshop.isOwner ? (
                <>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={workshop.isBusy || workshop.hasConsent}
                    onClick={() => void workshop.toggleConsent(true)}
                  >
                    {t("hub.ai.consent.enable")}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    disabled={workshop.isBusy || !workshop.hasConsent}
                    onClick={() => void workshop.toggleConsent(false)}
                  >
                    {t("hub.ai.consent.disable")}
                  </Button>
                </>
              ) : (
                <p className="text-xs text-muted-foreground">
                  {t("hub.ai.consent.owner_only")}
                </p>
              )}
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="flex flex-col gap-1.5 sm:col-span-2">
                <Label htmlFor="ai-objective">{t("hub.ai.form.objective")}</Label>
                <Textarea
                  id="ai-objective"
                  value={workshop.objective}
                  onChange={(event) => workshop.setObjective(event.target.value)}
                  className="min-h-[72px] bg-secondary text-sm"
                  placeholder={t("hub.ai.form.objective_example")}
                />
                <p className="text-[11px] text-muted-foreground">
                  {t("hub.ai.form.example_hint")}
                </p>
              </div>
              <div className="flex flex-col gap-1.5">
                <Label>{t("hub.ai.form.language")}</Label>
                <Select
                  value={workshop.language}
                  onValueChange={(value) =>
                    workshop.setLanguage(value as "fr" | "en")
                  }
                >
                  <SelectTrigger className="h-8 bg-secondary text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fr">{t("hub.ai.form.lang_fr")}</SelectItem>
                    <SelectItem value="en">{t("hub.ai.form.lang_en")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={
                  workshop.isBusy ||
                  !workshop.canAnalyze ||
                  !workshop.hasConsent ||
                  !workshop.objective.trim()
                }
                onClick={() => void workshop.startAnalysis()}
              >
                {workshop.polling ? (
                  <Loader2 aria-hidden className="size-3.5 animate-spin" />
                ) : (
                  <Wand2 aria-hidden className="size-3.5" />
                )}
                {t("hub.ai.form.generate")}
              </Button>
              {workshop.progressLabel ? (
                <span className="text-xs text-muted-foreground">
                  {workshop.progressLabel}
                </span>
              ) : null}
              {hasResults ? (
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  onClick={() => workshop.setView("results")}
                >
                  {t("hub.ai.nav.view_results")}
                </Button>
              ) : null}
            </div>
          </section>
        </>
      ) : null}

      {showResults && workshop.analysis?.status === "failed" ? (
        <section className="rounded-md border border-destructive/30 bg-destructive/10 p-4">
          <h2 className="mb-2 text-sm font-semibold text-destructive">
            {t("hub.ai.failed.title")}
          </h2>
          <p className="text-xs text-muted-foreground">{t("hub.ai.failed.text")}</p>
          {workshop.analysis.error_code ? (
            <p className="mt-2 text-[11px] text-muted-foreground">
              {workshop.analysis.error_code}
            </p>
          ) : null}
          <div className="mt-3 flex flex-wrap gap-1.5">
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => workshop.setView("compose")}
            >
              {t("hub.ai.nav.compose")}
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={workshop.clearResults}
            >
              {t("hub.ai.nav.new_analysis")}
            </Button>
          </div>
        </section>
      ) : null}

      {showResults && workshop.analysis?.status === "succeeded" && result ? (
        <div className="grid min-h-[520px] grid-cols-1 overflow-hidden rounded-md border border-border bg-card lg:grid-cols-12">
          <aside className="border-b border-border lg:col-span-4 lg:border-b-0 lg:border-r">
            <div className="border-b border-border px-3 py-2.5">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {t("hub.ai.result.suggestions")}
              </p>
              <p className="mt-1 line-clamp-2 text-[11px] text-muted-foreground">
                {result.summary || t("hub.ai.result.no_summary")}
              </p>
            </div>
            {workshop.suggestions.length === 0 ? (
              <p className="p-3 text-sm text-muted-foreground">
                {t("hub.ai.result.no_suggestions")}
              </p>
            ) : (
              <ul className="max-h-[60vh] overflow-y-auto lg:max-h-[calc(100%-4.5rem)]">
                {workshop.suggestions.map((suggestion, index) => {
                  const adoptedId = workshop.adoptedByIndex[index];
                  const active = selected?.index === index;
                  return (
                    <li key={`${suggestion.title}-${index}`}>
                      <button
                        type="button"
                        onClick={() => workshop.setSelectedSuggestion(index)}
                        className={cn(
                          "flex w-full flex-col gap-1 border-b border-border px-3 py-3 text-left transition-colors",
                          active
                            ? "bg-secondary/80"
                            : "hover:bg-secondary/40"
                        )}
                      >
                        <span className="flex items-start justify-between gap-2">
                          <span className="text-sm font-semibold text-foreground">
                            {suggestion.title}
                          </span>
                          {adoptedId != null ? (
                            <span className="inline-flex shrink-0 items-center gap-1 rounded-md border border-border bg-card px-1.5 py-0.5 text-[10px] font-medium text-success">
                              <Check aria-hidden className="size-3" />
                              {t("hub.ai.result.adopted_badge")}
                            </span>
                          ) : (
                            <span className="shrink-0 text-[10px] text-muted-foreground">
                              #{index + 1}
                            </span>
                          )}
                        </span>
                        <span className="line-clamp-2 text-[11px] text-muted-foreground">
                          {suggestion.description}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </aside>

          <section className="flex flex-col gap-4 p-4 lg:col-span-5">
            {selected ? (
              <>
                <div>
                  <h2 className="text-base font-semibold text-foreground">
                    {selected.item.title}
                  </h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {selected.item.description}
                  </p>
                </div>
                {selected.item.steps?.length ? (
                  <div>
                    <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                      {t("hub.ai.result.steps")}
                    </h3>
                    <ol className="list-decimal space-y-1 pl-5 text-xs text-foreground">
                      {selected.item.steps.map((step) => (
                        <li key={step}>{step}</li>
                      ))}
                    </ol>
                  </div>
                ) : null}
                {selected.item.acceptance_criteria?.length ? (
                  <div>
                    <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                      {t("hub.ai.result.criteria")}
                    </h3>
                    <ul className="list-disc space-y-1 pl-5 text-xs text-muted-foreground">
                      {selected.item.acceptance_criteria.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                <div className="mt-auto flex flex-wrap gap-1.5 border-t border-border pt-3">
                  {workshop.adoptedByIndex[selected.index] != null ? (
                    <>
                      <Button
                        type="button"
                        size="sm"
                        onClick={() =>
                          workshop.openTask(
                            workshop.adoptedByIndex[selected.index]
                          )
                        }
                      >
                        <ExternalLink aria-hidden className="size-3.5" />
                        {t("hub.ai.toasts.open_task")}
                      </Button>
                      <span className="self-center text-[11px] text-muted-foreground">
                        {t("hub.ai.result.adopted_keep")}
                      </span>
                    </>
                  ) : (
                    <Button
                      type="button"
                      size="sm"
                      disabled={workshop.isBusy || !workshop.canCreateTask}
                      onClick={() => void workshop.adopt(selected.index)}
                    >
                      {t("hub.ai.result.adopt")}
                    </Button>
                  )}
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                {t("hub.ai.result.no_suggestions")}
              </p>
            )}
          </section>

          <aside className="border-t border-border bg-secondary/20 p-4 lg:col-span-3 lg:border-l lg:border-t-0">
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {t("hub.ai.meta.title")}
            </h2>
            <dl className="flex flex-col gap-2 text-xs">
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">{t("hub.ai.meta.model")}</dt>
                <dd className="font-medium text-foreground">
                  {workshop.analysis.model}
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">{t("hub.ai.meta.sha")}</dt>
                <dd className="font-medium text-foreground">
                  {(workshop.analysis.commit_sha || "—").slice(0, 12)}
                </dd>
              </div>
              {workshop.currentSha ? (
                <div className="flex justify-between gap-2">
                  <dt className="text-muted-foreground">
                    {t("hub.ai.meta.current_sha")}
                  </dt>
                  <dd className="font-medium text-foreground">
                    {workshop.currentSha.slice(0, 12)}
                  </dd>
                </div>
              ) : null}
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">{t("hub.ai.meta.prompt")}</dt>
                <dd className="font-medium text-foreground">
                  {workshop.analysis.prompt_version || "—"}
                </dd>
              </div>
            </dl>

            {(result.entry_points?.length ?? 0) > 0 ? (
              <div className="mt-4">
                <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                  {t("hub.ai.result.entry_points")}
                </h3>
                <ul className="flex flex-col gap-1.5">
                  {result.entry_points.map((point, index) => {
                    const source = workshop.analysis?.sources?.find(
                      (item) => item.source_id === point.source_id
                    );
                    return (
                      <li
                        key={`${point.source_id}-${index}`}
                        className="rounded-md border border-border bg-card px-2 py-1.5 text-[11px]"
                      >
                        <span className="font-medium text-foreground">
                          {source?.path || point.source_id}
                        </span>
                        {point.line_start ? (
                          <span className="ml-1 text-muted-foreground">
                            L{point.line_start}
                            {point.line_end ? `–${point.line_end}` : ""}
                          </span>
                        ) : null}
                      </li>
                    );
                  })}
                </ul>
                <p className="mt-2 text-[10px] text-muted-foreground">
                  {workshop.isSourcesStale
                    ? t("hub.ai.result.sources_stale")
                    : t("hub.ai.result.sources_hint")}
                </p>
              </div>
            ) : null}

            {(result.unknowns?.length ?? 0) > 0 ? (
              <div className="mt-4">
                <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                  {t("hub.ai.result.unknowns")}
                </h3>
                <ul className="list-disc space-y-1 pl-4 text-[11px] text-muted-foreground">
                  {result.unknowns.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            <p className="mt-4 text-[10px] leading-relaxed text-muted-foreground">
              {t("hub.ai.meta.disclaimer")}
            </p>
          </aside>
        </div>
      ) : null}
    </div>
  );
}
