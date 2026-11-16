import { useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  CircleDot,
  Code2,
  ExternalLink,
  GitPullRequest,
  HelpCircle,
  Lock,
  Send,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { SelinaHubCta } from "@/models/ai/components/selina-hub-cta";
import { useSelinaHubContext } from "@/models/ai/components/use-selina-hub-context";
import { HubConfirmDialog } from "../components/hub-confirm-dialog";
import { useTaskContribution } from "../hooks/use-task-contribution";
import { SafeMarkdown } from "../functions/safe-markdown";

function parseCriteriaLines(text: string): string[] {
  return text
    .split("\n")
    .map((line) => line.replace(/^[-*]\s*/, "").trim())
    .filter(Boolean)
    .slice(0, 10);
}

function formatTaskDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function UserAvatar({ userId }: { userId: number }) {
  const tones = [
    "bg-brand/15 text-brand",
    "bg-success/15 text-success",
    "bg-warning-soft text-foreground",
    "bg-secondary text-muted-foreground",
  ];
  return (
    <span
      className={cn(
        "inline-flex size-8 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold",
        tones[Math.abs(userId) % tones.length]
      )}
      aria-hidden
    >
      {String(userId).slice(-2)}
    </span>
  );
}

export default function TaskContributionPage() {
  const { t } = useTranslation();
  const params = useParams();
  const projectId = Number(params.id);
  const taskId = Number(params.taskId);
  const detail = useTaskContribution(projectId, taskId);

  useSelinaHubContext(
    detail.project?.id,
    detail.project?.title,
    detail.task?.id,
    detail.task?.title
  );

  const [summary, setSummary] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [sha, setSha] = useState("");
  const [proposeMode, setProposeMode] = useState<"write" | "preview">("write");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [criteriaText, setCriteriaText] = useState("");
  const [confirmClose, setConfirmClose] = useState(false);

  useEffect(() => {
    if (!detail.task) return;
    setEditTitle(detail.task.title);
    setEditDescription(detail.task.description ?? "");
    setCriteriaText((detail.task.acceptance_criteria ?? []).join("\n"));
    // Resync uniquement quand l'identité ou la date de mise à jour change (pas à chaque nouvel objet).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [detail.task?.id, detail.task?.updated_at]);

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
  const canEditDraft = detail.canMaintain && task.status === "draft";
  const draftCriteria = parseCriteriaLines(criteriaText);
  const canOpenDraft = draftCriteria.length > 0 && editTitle.trim().length > 0;
  const contributions = detail.contributions?.results ?? [];

  const statusTone =
    task.status === "open"
      ? "border-transparent bg-success text-success-foreground"
      : task.status === "closed"
        ? "border-transparent bg-secondary text-muted-foreground"
        : "border-transparent bg-warning text-foreground";

  const buildDraftPayload = () => ({
    title: editTitle.trim(),
    description: editDescription.trim(),
    acceptance_criteria: draftCriteria,
  });

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-5">
      <Button asChild variant="ghost" className="h-8 w-fit gap-1.5 px-2 text-xs">
        <Link to={`/hub/projects/${project.id}?tab=contribute`}>
          <ArrowLeft aria-hidden className="size-3.5" />
          {t("hub.task.back_project")}
        </Link>
      </Button>

      {/* En-tête type ticket */}
      <header className="flex flex-col gap-4 border-b border-border pb-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            {canEditDraft ? (
              <Input
                value={editTitle}
                onChange={(event) => setEditTitle(event.target.value)}
                className="h-11 border-border bg-card text-2xl font-semibold tracking-tight"
                maxLength={180}
                aria-label={t("hub.task.edit.title_label")}
              />
            ) : (
              <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
                {task.title}{" "}
                <span className="font-normal text-muted-foreground">#{task.id}</span>
              </h1>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {detail.canMaintain && task.status === "open" ? (
              <Button asChild className="h-8 gap-1.5 rounded-md text-xs font-semibold">
                <Link to={`/hub/projects/${project.id}/reviews`}>
                  {t("hub.task.actions.review")}
                </Link>
              </Button>
            ) : null}
            {repositoryReady ? (
              <Button asChild variant="outline" className="h-8 gap-1.5 rounded-md text-xs">
                <Link to={`/hub/projects/${project.id}?tab=code`}>
                  <Code2 aria-hidden className="size-3.5" />
                  {t("hub.detail.actions.open_code")}
                </Link>
              </Button>
            ) : null}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
              statusTone
            )}
          >
            {task.status === "closed" ? (
              <Lock aria-hidden className="size-3.5" />
            ) : task.status === "open" ? (
              <CircleDot aria-hidden className="size-3.5" />
            ) : (
              <CircleDot aria-hidden className="size-3.5" />
            )}
            {t(`hub.detail.task_status.${task.status}`)}
          </span>
          <p className="text-sm text-muted-foreground">
            {t("hub.task.opened_meta", {
              author: t("hub.task.contributions.author", { id: task.created_by }),
              date: formatTaskDate(task.created_at),
              project: project.title,
            })}
          </p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        {/* Colonne principale */}
        <div className="flex min-w-0 flex-col gap-4">
          {/* Carte description */}
          <article className="overflow-hidden rounded-lg border border-border bg-card">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-secondary/40 px-4 py-2.5">
              <div className="flex min-w-0 items-center gap-2">
                <UserAvatar userId={task.created_by} />
                <p className="truncate text-sm">
                  <span className="font-semibold text-foreground">
                    {t("hub.task.contributions.author", { id: task.created_by })}
                  </span>{" "}
                  <span className="text-muted-foreground">
                    {t("hub.task.opened_ago", { date: formatTaskDate(task.created_at) })}
                  </span>
                </p>
              </div>
              {detail.canMaintain ? (
                <span className="rounded-full border border-border bg-card px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                  {t("hub.task.badges.maintainer")}
                </span>
              ) : null}
            </div>

            <div className="px-4 py-4">
              {canEditDraft ? (
                <div className="flex flex-col gap-3">
                  <Textarea
                    value={editDescription}
                    onChange={(event) => setEditDescription(event.target.value)}
                    placeholder={t("hub.task.edit.description_placeholder")}
                    className="min-h-[160px] bg-secondary text-sm"
                    maxLength={5000}
                  />
                  <div className="flex flex-wrap items-center gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      disabled={detail.isBusy || !editTitle.trim()}
                      className="h-8 rounded-md text-xs"
                      onClick={() => void detail.patchTask(buildDraftPayload())}
                    >
                      {t("hub.task.edit.save")}
                    </Button>
                    <Button
                      type="button"
                      disabled={detail.isBusy || !canOpenDraft}
                      className="h-8 rounded-md text-xs font-semibold"
                      onClick={() =>
                        void detail.patchTask({
                          ...buildDraftPayload(),
                          status: "open",
                        })
                      }
                    >
                      {t("hub.task.actions.open_task")}
                    </Button>
                  </div>
                  {!canOpenDraft ? (
                    <p className="text-xs text-muted-foreground">
                      {t("hub.task.criteria.required_to_open")}
                    </p>
                  ) : (
                    <p className="text-xs text-muted-foreground">{t("hub.task.edit.hint")}</p>
                  )}
                </div>
              ) : task.description ? (
                <div className="prose-sm max-w-none text-sm leading-relaxed text-foreground">
                  <SafeMarkdown content={task.description} />
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  {t("hub.task.no_description")}
                </p>
              )}
            </div>
          </article>

          {!detail.canMaintain && detail.firstStep ? (
            <div className="rounded-lg border border-border bg-card px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {t("hub.task.first_step.title")}
              </p>
              <p className="mt-1 text-sm text-foreground">{detail.firstStep}</p>
            </div>
          ) : null}

          {/* Timeline propositions */}
          <section className="flex flex-col gap-3">
            <h2 className="text-sm font-semibold text-foreground">
              {t("hub.task.contributions.title")}
            </h2>

            {detail.contributionsLoading ? (
              <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
            ) : contributions.length === 0 ? (
              <p className="rounded-lg border border-dashed border-border px-4 py-8 text-center text-sm text-muted-foreground">
                {t("hub.task.contributions.empty")}
              </p>
            ) : (
              <ul className="relative flex flex-col gap-3 border-l border-border pl-4">
                {contributions.map((item) => (
                  <li key={item.id} className="relative">
                    <span className="absolute -left-[21px] top-3 size-2.5 rounded-full border-2 border-card bg-border" />
                    <article className="overflow-hidden rounded-lg border border-border bg-card">
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-secondary/40 px-4 py-2.5">
                        <div className="flex min-w-0 items-center gap-2">
                          <UserAvatar userId={item.author_id} />
                          <p className="truncate text-sm">
                            <span className="font-semibold text-foreground">
                              {t("hub.task.contributions.author", {
                                id: item.author_id,
                              })}
                            </span>{" "}
                            <span className="text-muted-foreground">
                              {formatTaskDate(item.created_at)}
                            </span>
                          </p>
                        </div>
                        <span
                          className={cn(
                            "rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                            item.status === "accepted"
                              ? "bg-success/15 text-success"
                              : item.status === "rejected"
                                ? "bg-destructive/10 text-destructive"
                                : "bg-secondary text-muted-foreground"
                          )}
                        >
                          {t(`hub.task.contributions.status.${item.status}`)}
                        </span>
                      </div>
                      <div className="px-4 py-3 text-sm text-foreground">
                        <p>{item.summary}</p>
                        {item.pull_request_number ? (
                          <p className="mt-2 inline-flex items-center gap-1.5 rounded-md border border-border bg-secondary/50 px-2 py-1 text-xs text-foreground">
                            <GitPullRequest aria-hidden className="size-3.5 text-success" />
                            PR #{item.pull_request_number}
                          </p>
                        ) : null}
                      </div>
                    </article>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Aide forum */}
          {detail.helpDraft ? (
            <section className="rounded-lg border border-border bg-card p-4">
              <h2 className="mb-3 text-sm font-semibold text-foreground">
                {t("hub.task.help.title")}
              </h2>
              {detail.forumUnavailable ? (
                <p className="mb-3 rounded-md border border-warning/30 bg-warning-soft px-3 py-2 text-xs text-foreground">
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

          {/* Composer proposition */}
          {detail.showProposeCta ? (
            <section className="overflow-hidden rounded-lg border border-border bg-card">
              <div className="flex items-center justify-between border-b border-border px-3">
                <div className="flex gap-1">
                  <button
                    type="button"
                    className={cn(
                      "border-b-2 px-3 py-2 text-xs font-semibold transition-colors",
                      proposeMode === "write"
                        ? "border-brand text-foreground"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    )}
                    onClick={() => setProposeMode("write")}
                  >
                    {t("hub.task.propose.write")}
                  </button>
                  <button
                    type="button"
                    className={cn(
                      "border-b-2 px-3 py-2 text-xs font-semibold transition-colors",
                      proposeMode === "preview"
                        ? "border-brand text-foreground"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    )}
                    onClick={() => setProposeMode("preview")}
                  >
                    {t("hub.task.propose.preview")}
                  </button>
                </div>
              </div>

              <form
                className="flex flex-col gap-3 p-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  if (closed) return;
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
                        setProposeMode("write");
                      }
                    });
                }}
              >
                {closed ? (
                  <p className="text-sm text-destructive">
                    {t("hub.task.errors.task_closed")}
                  </p>
                ) : proposeMode === "write" ? (
                  <>
                    <Textarea
                      value={summary}
                      onChange={(event) => setSummary(event.target.value)}
                      placeholder={t("hub.task.propose.summary_placeholder")}
                      className="min-h-[120px] resize-y rounded-md border-border bg-background text-sm"
                      required
                    />
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
                  </>
                ) : (
                  <div className="min-h-[120px] rounded-md border border-border bg-background px-3 py-2 text-sm">
                    {summary.trim() ? (
                      <SafeMarkdown content={summary} />
                    ) : (
                      <p className="text-muted-foreground">
                        {t("hub.task.propose.preview_empty")}
                      </p>
                    )}
                  </div>
                )}

                <p className="text-xs text-muted-foreground">{t("hub.task.propose.hint")}</p>

                <div className="flex flex-wrap items-center justify-end gap-2">
                  <Button
                    type="submit"
                    disabled={detail.isBusy || closed || !summary.trim()}
                    className="h-8 gap-1.5 rounded-md text-xs font-semibold"
                  >
                    <Send aria-hidden className="size-3.5" />
                    {t("hub.task.propose.submit")}
                  </Button>
                </div>
              </form>
            </section>
          ) : null}

          {detail.canMaintain && task.status === "open" ? (
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3">
              <p className="text-xs text-muted-foreground">
                {t("hub.task.maintainer_hint")}
              </p>
              <Button
                type="button"
                variant="outline"
                disabled={detail.isBusy}
                className="h-8 gap-1.5 rounded-md text-xs"
                onClick={() => setConfirmClose(true)}
              >
                <CheckCircle2 aria-hidden className="size-3.5" />
                {t("hub.task.actions.close_task")}
              </Button>
            </div>
          ) : null}
        </div>

        {/* Sidebar */}
        <aside className="flex flex-col gap-0 lg:sticky lg:top-4 lg:self-start">
          <SidebarBlock title={t("hub.task.criteria.title")}>
            {canEditDraft ? (
              <div className="flex flex-col gap-2">
                <Textarea
                  value={criteriaText}
                  onChange={(event) => setCriteriaText(event.target.value)}
                  placeholder={t("hub.task.criteria.placeholder")}
                  className="min-h-[110px] bg-secondary text-xs"
                />
                <p className="text-[11px] text-muted-foreground">
                  {t("hub.task.criteria.hint")}
                </p>
              </div>
            ) : criteria.length === 0 ? (
              <p className="text-xs text-muted-foreground">{t("hub.task.criteria.empty")}</p>
            ) : (
              <ul className="flex flex-col gap-2">
                {criteria.map((item, index) => (
                  <li
                    key={`${index}-${item.slice(0, 24)}`}
                    className="flex items-start gap-2 text-xs text-foreground"
                  >
                    <span className="mt-0.5 inline-flex size-3.5 shrink-0 rounded-sm border border-border" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </SidebarBlock>

          <SidebarBlock title={t("hub.task.sidebar.development")}>
            {repositoryReady ? (
              <Link
                to={`/hub/projects/${project.id}?tab=code`}
                className="inline-flex items-center gap-1.5 text-xs font-medium text-brand hover:underline"
              >
                <Code2 aria-hidden className="size-3.5" />
                {t("hub.detail.actions.open_code")}
              </Link>
            ) : (
              <p className="text-xs text-muted-foreground">
                {t("hub.task.sidebar.no_repo")}
              </p>
            )}
            {contributions.some((item) => item.pull_request_number) ? (
              <ul className="mt-2 flex flex-col gap-1.5">
                {contributions
                  .filter((item) => item.pull_request_number)
                  .map((item) => (
                    <li
                      key={`pr-${item.id}`}
                      className="inline-flex items-center gap-1.5 text-xs text-foreground"
                    >
                      <GitPullRequest aria-hidden className="size-3.5 text-success" />
                      PR #{item.pull_request_number}
                    </li>
                  ))}
              </ul>
            ) : null}
          </SidebarBlock>

          {sources.length > 0 ? (
            <SidebarBlock title={t("hub.task.sources.title")}>
              <p className="mb-2 text-[11px] text-muted-foreground">
                {t("hub.task.sources.hint")}
              </p>
              <ul className="flex flex-col gap-1.5">
                {sources.map((source, index) => (
                  <li key={`${source.path}-${index}`} className="text-xs">
                    {source.url ? (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 font-medium text-brand hover:underline"
                      >
                        <span className="truncate">{source.path}</span>
                        <ExternalLink aria-hidden className="size-3 shrink-0" />
                      </a>
                    ) : (
                      <span className="text-foreground">{source.path}</span>
                    )}
                  </li>
                ))}
              </ul>
            </SidebarBlock>
          ) : null}

          <SidebarBlock title={t("hub.task.sidebar.actions")} last>
            <div className="flex flex-col gap-2">
              {detail.access.canDiscuss && !detail.canMaintain ? (
                <Button
                  type="button"
                  variant="outline"
                  className="h-8 justify-start gap-1.5 rounded-md text-xs"
                  onClick={detail.openHelpDraft}
                >
                  <HelpCircle aria-hidden className="size-3.5" />
                  {t("hub.task.actions.ask_help")}
                </Button>
              ) : null}
              {detail.canMaintain && task.status === "open" ? (
                <Button asChild variant="outline" className="h-8 justify-start rounded-md text-xs">
                  <Link to={`/hub/projects/${project.id}/reviews`}>
                    {t("hub.task.actions.review")}
                  </Link>
                </Button>
              ) : null}
              {!detail.access.canDiscuss || detail.canMaintain ? (
                <p className="text-xs text-muted-foreground">
                  {t("hub.task.project_label", { title: project.title })}
                </p>
              ) : null}
            </div>
          </SidebarBlock>
        </aside>
      </div>

      <SelinaHubCta />

      <HubConfirmDialog
        open={confirmClose}
        title={t("hub.task.actions.close_task")}
        description={t("hub.task.confirm.close")}
        confirmLabel={t("hub.task.actions.close_task")}
        destructive
        busy={detail.isBusy}
        onOpenChange={setConfirmClose}
        onConfirm={() => {
          void detail
            .patchTask({ status: "closed" })
            .finally(() => setConfirmClose(false));
        }}
      />
    </div>
  );
}

function SidebarBlock({
  title,
  children,
  last = false,
}: {
  title: string;
  children: ReactNode;
  last?: boolean;
}) {
  return (
    <div className={cn("py-4", !last && "border-b border-border")}>
      <h3 className="mb-2 text-xs font-semibold text-muted-foreground">{title}</h3>
      {children}
    </div>
  );
}
