import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AlertTriangle,
  ArrowLeft,
  CheckSquare,
  Code2,
  ExternalLink,
  HelpCircle,
  Send,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useTaskContribution } from "../hooks/use-task-contribution";

export default function TaskContributionPage() {
  const { t } = useTranslation();
  const params = useParams();
  const projectId = Number(params.id);
  const taskId = Number(params.taskId);
  const detail = useTaskContribution(projectId, taskId);

  const [summary, setSummary] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [sha, setSha] = useState("");
  const [showPropose, setShowPropose] = useState(false);

  if (!Number.isFinite(projectId) || !Number.isFinite(taskId)) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center text-sm text-muted-foreground">
        {t("hub.task.errors.not_found")}
      </div>
    );
  }

  if (detail.isLoading && !detail.task) {
    return (
      <div className="mx-auto max-w-3xl py-16 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </div>
    );
  }

  if (detail.isError || !detail.task || !detail.project) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">
          {detail.errorStatus === 403
            ? t("hub.task.errors.forbidden")
            : t("hub.task.errors.not_found")}
        </p>
        <Button asChild variant="outline" className="h-9 text-xs">
          <Link to={`/hub/projects/${projectId}`}>
            <ArrowLeft aria-hidden className="mr-1 size-3.5" />
            {t("hub.task.back_project")}
          </Link>
        </Button>
      </div>
    );
  }

  if (detail.task.project_id !== projectId) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">{t("hub.task.errors.mismatch")}</p>
        <Button asChild variant="outline" className="h-9 text-xs">
          <Link to={`/hub/projects/${detail.task.project_id}/tasks/${detail.task.id}`}>
            {t("hub.task.goto_correct")}
          </Link>
        </Button>
      </div>
    );
  }

  const task = detail.task;
  const project = detail.project;
  const repositoryReady = project.repository?.status === "ready";
  const criteria = task.acceptance_criteria ?? [];
  const sources = task.source_references ?? [];
  const closed = task.status === "closed";

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" className="h-8 gap-1.5 px-2 text-xs">
          <Link to={`/hub/projects/${project.id}?tab=contribute`}>
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.task.back_project")}
          </Link>
        </Button>
        <span className="rounded bg-secondary px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
          {t(`hub.detail.task_status.${task.status}`)}
        </span>
      </div>

      <header className="flex flex-col gap-3 border-b border-border pb-5">
        <p className="text-xs text-muted-foreground">
          {t("hub.task.project_label", { title: project.title })}
        </p>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          {task.title}
        </h1>
        <p className="max-w-3xl whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
          {task.description || t("hub.task.no_description")}
        </p>
        <div className="flex flex-wrap gap-2">
          {repositoryReady ? (
            <Button asChild variant="outline" className="h-9 gap-1.5 rounded-lg text-xs">
              <Link to={`/hub/projects/${project.id}?tab=code`}>
                <Code2 aria-hidden className="size-3.5" />
                {t("hub.detail.actions.open_code")}
              </Link>
            </Button>
          ) : null}
          {detail.access.canDiscuss ? (
            <Button
              type="button"
              variant="outline"
              className="h-9 gap-1.5 rounded-lg text-xs"
              onClick={detail.openHelpDraft}
            >
              <HelpCircle aria-hidden className="size-3.5" />
              {t("hub.task.actions.ask_help")}
            </Button>
          ) : null}
          {detail.canSubmit ? (
            <Button
              type="button"
              className="h-9 gap-1.5 rounded-lg text-xs"
              onClick={() => setShowPropose(true)}
            >
              <Send aria-hidden className="size-3.5" />
              {t("hub.task.actions.propose")}
            </Button>
          ) : null}
          {detail.canMaintain && task.status === "draft" ? (
            <Button
              type="button"
              variant="secondary"
              disabled={detail.isBusy || criteria.length === 0}
              className="h-9 rounded-lg text-xs"
              onClick={() => void detail.patchTask({ status: "open" })}
            >
              {t("hub.task.actions.open_task")}
            </Button>
          ) : null}
          {detail.canMaintain && task.status === "open" ? (
            <Button
              type="button"
              variant="outline"
              disabled={detail.isBusy}
              className="h-9 rounded-lg text-xs"
              onClick={() => {
                if (window.confirm(t("hub.task.confirm.close"))) {
                  void detail.patchTask({ status: "closed" });
                }
              }}
            >
              {t("hub.task.actions.close_task")}
            </Button>
          ) : null}
        </div>
      </header>

      {detail.firstStep ? (
        <section className="rounded-2xl border border-brand/30 bg-brand-soft/50 p-5 shadow-card">
          <h2 className="mb-2 text-sm font-bold text-foreground">
            {t("hub.task.first_step.title")}
          </h2>
          <p className="text-sm leading-relaxed text-muted-foreground">
            {detail.firstStep}
          </p>
        </section>
      ) : null}

      <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
        <h2 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <CheckSquare aria-hidden className="size-4 text-brand" />
          {t("hub.task.criteria.title")}
        </h2>
        {criteria.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("hub.task.criteria.empty")}</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {criteria.map((item, index) => (
              <li
                key={`${index}-${item.slice(0, 24)}`}
                className="flex items-start gap-2 rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm text-foreground"
              >
                <span className="mt-0.5 text-xs font-semibold text-muted-foreground">
                  {index + 1}.
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-3 text-xs text-muted-foreground">{t("hub.task.criteria.hint")}</p>
      </section>

      {sources.length > 0 ? (
        <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
          <h2 className="mb-2 text-sm font-bold text-foreground">
            {t("hub.task.sources.title")}
          </h2>
          <p className="mb-3 text-xs text-muted-foreground">{t("hub.task.sources.hint")}</p>
          <ul className="flex flex-col gap-2">
            {sources.map((source, index) => (
              <li key={`${source.path}-${index}`} className="text-sm">
                {source.url ? (
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 font-medium text-brand hover:underline"
                  >
                    {source.path}
                    <ExternalLink aria-hidden className="size-3.5" />
                  </a>
                ) : (
                  <span className="text-foreground">{source.path}</span>
                )}
                {source.commit_sha ? (
                  <span className="ml-2 text-xs text-muted-foreground">
                    {source.commit_sha.slice(0, 8)}
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {detail.helpDraft ? (
        <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
          <h2 className="mb-3 text-sm font-bold text-foreground">
            {t("hub.task.help.title")}
          </h2>
          {detail.forumUnavailable ? (
            <p className="mb-3 rounded-lg border border-warning/30 bg-warning-soft px-3 py-2 text-xs text-foreground">
              {t("hub.task.help.forum_kept")}
            </p>
          ) : null}
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="help-title">{t("hub.task.help.field_title")}</Label>
              <Input
                id="help-title"
                value={detail.helpDraft.title}
                onChange={(event) =>
                  detail.setHelpDraft({
                    ...detail.helpDraft!,
                    title: event.target.value,
                  })
                }
                className="h-9 bg-secondary"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="help-body">{t("hub.task.help.field_body")}</Label>
              <Textarea
                id="help-body"
                value={detail.helpDraft.body}
                onChange={(event) =>
                  detail.setHelpDraft({
                    ...detail.helpDraft!,
                    body: event.target.value,
                  })
                }
                className="min-h-[100px] bg-secondary text-sm"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                className="h-8 text-xs"
                onClick={detail.closeHelpDraft}
              >
                {t("common.cancel")}
              </Button>
              <Button
                type="button"
                className="h-8 text-xs"
                disabled={detail.isBusy}
                onClick={() => void detail.publishHelp()}
              >
                {t("hub.task.help.publish")}
              </Button>
            </div>
          </div>
        </section>
      ) : null}

      {showPropose ? (
        <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
          <h2 className="mb-2 text-sm font-bold text-foreground">
            {t("hub.task.propose.title")}
          </h2>
          <p className="mb-4 text-xs text-muted-foreground">
            {t("hub.task.propose.hint")}
          </p>
          {closed ? (
            <p className="text-sm text-destructive">{t("hub.task.errors.task_closed")}</p>
          ) : (
            <form
              className="flex flex-col gap-3"
              onSubmit={(event) => {
                event.preventDefault();
                void detail
                  .proposeWork({
                    summary,
                    pull_request_number: prNumber ? Number(prNumber) : null,
                    artifact_sha: sha || null,
                  })
                  .then((ok) => {
                    if (ok) {
                      setSummary("");
                      setPrNumber("");
                      setSha("");
                      setShowPropose(false);
                    }
                  });
              }}
            >
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="contrib-summary">{t("hub.task.propose.summary")}</Label>
                <Textarea
                  id="contrib-summary"
                  value={summary}
                  onChange={(event) => setSummary(event.target.value)}
                  className="min-h-[90px] bg-secondary text-sm"
                  required
                />
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="contrib-pr">{t("hub.task.propose.pr")}</Label>
                  <Input
                    id="contrib-pr"
                    type="number"
                    min={1}
                    value={prNumber}
                    onChange={(event) => setPrNumber(event.target.value)}
                    className="h-9 bg-secondary"
                    placeholder={t("hub.task.propose.pr_optional")}
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="contrib-sha">{t("hub.task.propose.sha")}</Label>
                  <Input
                    id="contrib-sha"
                    value={sha}
                    onChange={(event) => setSha(event.target.value)}
                    className="h-9 bg-secondary"
                    placeholder={t("hub.task.propose.sha_optional")}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="h-8 text-xs"
                  onClick={() => setShowPropose(false)}
                >
                  {t("common.cancel")}
                </Button>
                <Button
                  type="submit"
                  disabled={detail.isBusy || !summary.trim()}
                  className="h-8 text-xs"
                >
                  {t("hub.task.propose.submit")}
                </Button>
              </div>
            </form>
          )}
        </section>
      ) : null}

      <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
        <h2 className="mb-3 text-sm font-bold text-foreground">
          {t("hub.task.contributions.title")}
        </h2>
        {detail.contributionsLoading ? (
          <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
        ) : !detail.contributions || detail.contributions.results.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {t("hub.task.contributions.empty")}
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {detail.contributions.results.map((item) => (
              <li
                key={item.id}
                className="rounded-xl border border-border bg-secondary/40 px-4 py-3 text-sm"
              >
                <div className="mb-1 flex flex-wrap items-center gap-2">
                  <span className="rounded bg-card px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                    {t(`hub.task.contributions.status.${item.status}`)}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {t("hub.task.contributions.author", { id: item.author_id })}
                  </span>
                </div>
                <p className="text-foreground">{item.summary}</p>
                {item.pull_request_number ? (
                  <p className="mt-1 text-xs text-muted-foreground">
                    PR #{item.pull_request_number}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
