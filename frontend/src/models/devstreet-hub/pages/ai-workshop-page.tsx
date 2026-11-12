import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AlertTriangle,
  ArrowLeft,
  Loader2,
  Sparkles,
  Wand2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAiWorkshop } from "../hooks/use-ai-workshop";

export default function AiWorkshopPage() {
  const { t } = useTranslation();
  const params = useParams();
  const projectId = Number(params.id);
  const workshop = useAiWorkshop(projectId);
  const [manualOpen, setManualOpen] = useState(false);
  const [manualTitle, setManualTitle] = useState("");
  const [manualDescription, setManualDescription] = useState("");

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
        <Button asChild variant="outline" className="h-9 text-xs">
          <Link to="/hub/projects">
            <ArrowLeft aria-hidden className="mr-1 size-3.5" />
            {t("hub.upcoming.back")}
          </Link>
        </Button>
      </div>
    );
  }

  const project = workshop.project;
  const result = workshop.result;
  const suggestions = result?.suggested_tasks ?? [];

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" className="h-8 gap-1.5 px-2 text-xs">
          <Link to={`/hub/projects/${project.id}`}>
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.ai.back_project")}
          </Link>
        </Button>
        <h1 className="flex items-center gap-2 text-xl font-bold tracking-tight text-foreground sm:text-2xl">
          <Sparkles aria-hidden className="size-5 text-brand" />
          {t("hub.ai.title")}
        </h1>
      </div>

      <p className="max-w-3xl text-sm text-muted-foreground">{t("hub.ai.description")}</p>

      <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
        <h2 className="mb-2 text-sm font-bold text-foreground">
          {t("hub.ai.consent.title")}
        </h2>
        <p className="mb-4 text-xs leading-relaxed text-muted-foreground">
          {t("hub.ai.consent.text")}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-md bg-secondary px-2.5 py-1 text-xs font-medium text-foreground">
            {workshop.hasConsent
              ? t("hub.ai.consent.enabled")
              : t("hub.ai.consent.disabled")}
          </span>
          {workshop.isOwner ? (
            <>
              <Button
                type="button"
                disabled={workshop.isBusy}
                className="h-8 rounded-lg text-xs"
                onClick={() => void workshop.toggleConsent(true)}
              >
                {t("hub.ai.consent.enable")}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={workshop.isBusy}
                className="h-8 rounded-lg text-xs"
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
      </section>

      <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
        <h2 className="mb-3 text-sm font-bold text-foreground">
          {t("hub.ai.form.title")}
        </h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <Label htmlFor="ai-objective">{t("hub.ai.form.objective")}</Label>
            <Textarea
              id="ai-objective"
              value={workshop.objective}
              onChange={(event) => workshop.setObjective(event.target.value)}
              className="min-h-[88px] bg-secondary text-sm"
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
              <SelectTrigger className="h-10 rounded-lg bg-secondary text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fr">{t("hub.ai.form.lang_fr")}</SelectItem>
                <SelectItem value="en">{t("hub.ai.form.lang_en")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button
            type="button"
            disabled={
              workshop.isBusy ||
              !workshop.canAnalyze ||
              !workshop.hasConsent ||
              !workshop.objective.trim()
            }
            className="h-9 gap-1.5 rounded-lg text-xs"
            onClick={() => void workshop.startAnalysis()}
          >
            {workshop.polling ? (
              <Loader2 aria-hidden className="size-3.5 animate-spin" />
            ) : (
              <Wand2 aria-hidden className="size-3.5" />
            )}
            {t("hub.ai.form.generate")}
          </Button>
          <Button
            type="button"
            variant="outline"
            className="h-9 rounded-lg text-xs"
            onClick={() => setManualOpen((value) => !value)}
          >
            {t("hub.ai.form.manual")}
          </Button>
        </div>
        {workshop.progressLabel ? (
          <p className="mt-3 text-xs font-medium text-muted-foreground">
            {workshop.progressLabel}
          </p>
        ) : null}
      </section>

      {manualOpen ? (
        <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
          <h2 className="mb-3 text-sm font-bold text-foreground">
            {t("hub.ai.manual.title")}
          </h2>
          <p className="mb-3 text-xs text-muted-foreground">
            {t("hub.ai.manual.hint")}
          </p>
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="manual-title">{t("hub.detail.task_form.name")}</Label>
              <Input
                id="manual-title"
                value={manualTitle}
                onChange={(event) => setManualTitle(event.target.value)}
                className="h-9 bg-secondary"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="manual-desc">
                {t("hub.detail.task_form.description")}
              </Label>
              <Textarea
                id="manual-desc"
                value={manualDescription}
                onChange={(event) => setManualDescription(event.target.value)}
                className="min-h-[80px] bg-secondary text-sm"
              />
            </div>
            <div className="flex justify-end">
              <Button
                type="button"
                disabled={workshop.isBusy || !manualTitle.trim()}
                className="h-8 text-xs"
                onClick={() =>
                  void workshop
                    .createManual({
                      title: manualTitle.trim(),
                      description: manualDescription.trim(),
                    })
                    .then((ok) => {
                      if (ok) {
                        setManualTitle("");
                        setManualDescription("");
                        setManualOpen(false);
                      }
                    })
                }
              >
                {t("hub.ai.manual.submit")}
              </Button>
            </div>
          </div>
        </section>
      ) : null}

      {workshop.analysis?.status === "failed" ? (
        <section className="rounded-2xl border border-destructive/30 bg-destructive/10 p-5">
          <h2 className="mb-2 text-sm font-bold text-destructive">
            {t("hub.ai.failed.title")}
          </h2>
          <p className="text-xs text-muted-foreground">{t("hub.ai.failed.text")}</p>
          {workshop.analysis.error_code ? (
            <p className="mt-2 text-[11px] text-muted-foreground">
              {workshop.analysis.error_code}
            </p>
          ) : null}
        </section>
      ) : null}

      {workshop.analysis?.status === "succeeded" && result ? (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
          <section className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-card lg:col-span-8">
            <h2 className="text-sm font-bold text-foreground">
              {t("hub.ai.result.summary")}
            </h2>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
              {result.summary || t("hub.ai.result.no_summary")}
            </p>

            {(result.entry_points?.length ?? 0) > 0 ? (
              <div>
                <h3 className="mb-2 text-xs font-bold uppercase tracking-wide text-muted-foreground">
                  {t("hub.ai.result.entry_points")}
                </h3>
                <ul className="flex flex-col gap-2">
                  {result.entry_points.map((point, index) => {
                    const source = workshop.analysis?.sources?.find(
                      (item) => item.source_id === point.source_id
                    );
                    return (
                      <li
                        key={`${point.source_id}-${index}`}
                        className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs"
                      >
                        <span className="font-semibold text-foreground">
                          {source?.path || point.source_id}
                        </span>
                        {point.line_start ? (
                          <span className="ml-2 text-muted-foreground">
                            L{point.line_start}
                            {point.line_end ? `–${point.line_end}` : ""}
                          </span>
                        ) : null}
                        {point.reason ? (
                          <p className="mt-1 text-muted-foreground">{point.reason}</p>
                        ) : null}
                      </li>
                    );
                  })}
                </ul>
                {workshop.isSourcesStale ? (
                  <p className="mt-2 text-[11px] text-warning">
                    {t("hub.ai.result.sources_stale")}
                  </p>
                ) : (
                  <p className="mt-2 text-[11px] text-muted-foreground">
                    {t("hub.ai.result.sources_hint")}
                  </p>
                )}
              </div>
            ) : null}

            {(result.unknowns?.length ?? 0) > 0 ? (
              <div>
                <h3 className="mb-2 text-xs font-bold uppercase tracking-wide text-muted-foreground">
                  {t("hub.ai.result.unknowns")}
                </h3>
                <ul className="list-disc space-y-1 pl-5 text-xs text-muted-foreground">
                  {result.unknowns.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            <div>
              <h3 className="mb-3 text-xs font-bold uppercase tracking-wide text-muted-foreground">
                {t("hub.ai.result.suggestions")}
              </h3>
              {suggestions.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {t("hub.ai.result.no_suggestions")}
                </p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {suggestions.map((suggestion, index) => (
                    <li
                      key={`${suggestion.title}-${index}`}
                      className="rounded-xl border border-border bg-secondary/30 p-4"
                    >
                      <h4 className="mb-1 text-sm font-bold text-foreground">
                        {suggestion.title}
                      </h4>
                      <p className="mb-2 text-xs text-muted-foreground">
                        {suggestion.description}
                      </p>
                      {suggestion.steps?.length ? (
                        <ol className="mb-2 list-decimal space-y-1 pl-5 text-xs text-foreground">
                          {suggestion.steps.map((step) => (
                            <li key={step}>{step}</li>
                          ))}
                        </ol>
                      ) : null}
                      {suggestion.acceptance_criteria?.length ? (
                        <ul className="mb-3 list-disc space-y-1 pl-5 text-xs text-muted-foreground">
                          {suggestion.acceptance_criteria.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      ) : null}
                      <Button
                        type="button"
                        disabled={workshop.isBusy || !workshop.canCreateTask}
                        className="h-8 rounded-lg text-xs"
                        onClick={() => void workshop.adopt(index)}
                      >
                        {t("hub.ai.result.adopt")}
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <aside className="rounded-2xl border border-border bg-card p-5 shadow-card lg:col-span-4">
            <h2 className="mb-3 text-sm font-bold text-foreground">
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
            <p className="mt-4 text-[11px] leading-relaxed text-muted-foreground">
              {t("hub.ai.meta.disclaimer")}
            </p>
          </aside>
        </div>
      ) : null}
    </div>
  );
}
