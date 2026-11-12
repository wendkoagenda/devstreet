import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ExternalLink,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { pageCountOf, PAGE_SIZE } from "@/helpers/api/pagination";
import { cn } from "@/lib/utils";
import { useContributionReview } from "../hooks/use-contribution-review";

export default function ContributionReviewPage() {
  const { t } = useTranslation();
  const params = useParams();
  const projectId = Number(params.id);
  const review = useContributionReview(projectId);
  const [note, setNote] = useState("");

  if (!Number.isFinite(projectId) || projectId <= 0) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center text-sm text-muted-foreground">
        {t("hub.review.errors.not_found")}
      </div>
    );
  }

  if (review.isLoading && !review.project) {
    return (
      <div className="mx-auto max-w-3xl py-16 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </div>
    );
  }

  if (review.isError || !review.project) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">
          {review.errorStatus === 403
            ? t("hub.review.errors.forbidden")
            : t("hub.review.errors.not_found")}
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

  const project = review.project;
  const selected = review.selected;
  const pageCount = pageCountOf(review.contributions?.count ?? 0, PAGE_SIZE);
  const isAuthor =
    selected != null &&
    review.access.userId != null &&
    selected.author_id === review.access.userId;
  const canDecide =
    review.canReview &&
    selected?.status === "submitted" &&
    !isAuthor;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" className="h-8 gap-1.5 px-2 text-xs">
          <Link to={`/hub/projects/${project.id}`}>
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.review.back_project")}
          </Link>
        </Button>
        <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
          {t("hub.review.title", { title: project.title })}
        </h1>
      </div>

      <p className="max-w-3xl text-sm text-muted-foreground">
        {t("hub.review.description")}
      </p>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <aside className="flex flex-col gap-3 lg:col-span-4">
          <h2 className="text-sm font-bold text-foreground">
            {t("hub.review.list_title")}
          </h2>
          {review.listLoading ? (
            <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
          ) : !review.contributions || review.contributions.results.length === 0 ? (
            <p className="rounded-xl border border-dashed border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground">
              {t("hub.review.empty")}
            </p>
          ) : (
            <ul className="flex flex-col gap-2">
              {review.contributions.results.map((item) => {
                const active = item.id === review.activeId;
                return (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => {
                        setNote("");
                        review.selectContribution(item);
                      }}
                      className={cn(
                        "w-full rounded-xl border px-3 py-3 text-left transition-colors",
                        active
                          ? "border-brand/40 bg-brand-soft/50"
                          : "border-border bg-card hover:bg-secondary/60"
                      )}
                    >
                      <div className="mb-1 flex items-center gap-2">
                        <span className="rounded bg-secondary px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                          {t(`hub.task.contributions.status.${item.status}`)}
                        </span>
                        <span className="text-[11px] text-muted-foreground">
                          #{item.id}
                        </span>
                      </div>
                      <p className="line-clamp-2 text-xs font-medium text-foreground">
                        {item.summary}
                      </p>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}

          {pageCount > 1 ? (
            <div className="flex items-center justify-between gap-2 text-xs">
              <Button
                type="button"
                variant="outline"
                disabled={review.page <= 1}
                onClick={() => review.setPage(review.page - 1)}
                className="h-8 rounded-lg"
              >
                {t("pagination.previous")}
              </Button>
              <span className="text-muted-foreground">
                {t("hub.detail.page_of", {
                  page: review.page,
                  pageCount,
                })}
              </span>
              <Button
                type="button"
                variant="outline"
                disabled={review.page >= pageCount}
                onClick={() => review.setPage(review.page + 1)}
                className="h-8 rounded-lg"
              >
                {t("pagination.next")}
              </Button>
            </div>
          ) : null}
        </aside>

        <div className="flex flex-col gap-4 lg:col-span-8">
          {!selected ? (
            <p className="rounded-xl border border-dashed border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
              {t("hub.review.select_hint")}
            </p>
          ) : (
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
                <h2 className="mb-3 text-sm font-bold text-foreground">
                  {t("hub.review.panel.proposal")}
                </h2>
                <dl className="mb-4 flex flex-col gap-2 text-xs">
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">{t("hub.review.panel.author")}</dt>
                    <dd className="font-medium text-foreground">
                      #{selected.author_id}
                    </dd>
                  </div>
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">{t("hub.review.panel.task")}</dt>
                    <dd>
                      <Link
                        to={`/hub/projects/${project.id}/tasks/${selected.task_id}`}
                        className="font-medium text-brand hover:underline"
                      >
                        #{selected.task_id}
                      </Link>
                    </dd>
                  </div>
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">{t("hub.review.panel.status")}</dt>
                    <dd className="font-medium text-foreground">
                      {t(`hub.task.contributions.status.${selected.status}`)}
                    </dd>
                  </div>
                </dl>
                <p className="mb-4 whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                  {selected.summary}
                </p>
                <div className="flex flex-wrap gap-2">
                  {review.prUrl ? (
                    <Button
                      asChild
                      variant="outline"
                      className="h-8 gap-1.5 rounded-lg text-xs"
                    >
                      <a href={review.prUrl} target="_blank" rel="noopener noreferrer">
                        <ExternalLink aria-hidden className="size-3.5" />
                        {t("hub.review.panel.open_pr", {
                          number: selected.pull_request_number,
                        })}
                      </a>
                    </Button>
                  ) : selected.pull_request_number ? (
                    <span className="text-xs text-muted-foreground">
                      PR #{selected.pull_request_number}
                    </span>
                  ) : (
                    <span className="text-xs text-muted-foreground">
                      {t("hub.review.panel.no_pr")}
                    </span>
                  )}
                  {selected.artifact_sha ? (
                    <span className="rounded bg-secondary px-2 py-1 text-[11px] text-muted-foreground">
                      SHA {selected.artifact_sha.slice(0, 12)}
                    </span>
                  ) : null}
                </div>

                {selected.status !== "submitted" ? (
                  <div className="mt-4 rounded-lg border border-border bg-secondary/50 p-3 text-xs">
                    <p className="font-semibold text-foreground">
                      {selected.status === "accepted"
                        ? t("hub.review.decided.accepted", {
                            id: selected.reviewed_by_id ?? "—",
                          })
                        : t("hub.review.decided.rejected", {
                            id: selected.reviewed_by_id ?? "—",
                          })}
                    </p>
                    {selected.reviewed_at ? (
                      <p className="mt-1 text-muted-foreground">
                        {new Date(selected.reviewed_at).toLocaleString()}
                      </p>
                    ) : null}
                    {selected.review_note ? (
                      <p className="mt-2 whitespace-pre-wrap text-foreground">
                        {selected.review_note}
                      </p>
                    ) : null}
                  </div>
                ) : null}
              </section>

              <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
                <h2 className="mb-3 text-sm font-bold text-foreground">
                  {t("hub.review.panel.criteria")}
                </h2>
                {review.taskLoading ? (
                  <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
                ) : !review.task ? (
                  <p className="text-sm text-muted-foreground">
                    {t("hub.review.panel.criteria_missing")}
                  </p>
                ) : (review.task.acceptance_criteria ?? []).length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    {t("hub.task.criteria.empty")}
                  </p>
                ) : (
                  <ul className="mb-4 flex flex-col gap-2">
                    {review.task.acceptance_criteria.map((item, index) => (
                      <li
                        key={`${index}-${item.slice(0, 20)}`}
                        className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm"
                      >
                        <span className="mr-2 text-xs font-semibold text-muted-foreground">
                          {index + 1}.
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                )}

                {canDecide ? (
                  <div className="flex flex-col gap-3 border-t border-border pt-4">
                    <div className="flex flex-col gap-1.5">
                      <Label htmlFor="review-note">
                        {t("hub.review.form.note")} <span className="text-brand">*</span>
                      </Label>
                      <Textarea
                        id="review-note"
                        value={note}
                        onChange={(event) => setNote(event.target.value)}
                        className="min-h-[100px] bg-secondary text-sm"
                        required
                      />
                    </div>
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <Button
                        type="button"
                        disabled={review.isBusy || !note.trim()}
                        className="h-9 flex-1 gap-1.5 rounded-lg text-xs"
                        onClick={() =>
                          void review.decide({ status: "accepted", note }).then((ok) => {
                            if (ok) setNote("");
                          })
                        }
                      >
                        <CheckCircle2 aria-hidden className="size-3.5" />
                        {t("hub.review.form.accept")}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        disabled={review.isBusy || !note.trim()}
                        className="h-9 flex-1 gap-1.5 rounded-lg text-xs text-destructive"
                        onClick={() =>
                          void review.decide({ status: "rejected", note }).then((ok) => {
                            if (ok) setNote("");
                          })
                        }
                      >
                        <XCircle aria-hidden className="size-3.5" />
                        {t("hub.review.form.reject")}
                      </Button>
                    </div>
                    <p className="text-[11px] text-muted-foreground">
                      {t("hub.review.form.no_merge")}
                    </p>
                  </div>
                ) : isAuthor ? (
                  <p className="border-t border-border pt-4 text-xs text-muted-foreground">
                    {t("hub.review.self_notice")}
                  </p>
                ) : selected.status !== "submitted" ? (
                  <p className="border-t border-border pt-4 text-xs text-muted-foreground">
                    {t("hub.review.readonly_notice")}
                  </p>
                ) : !review.canReview ? (
                  <p className="border-t border-border pt-4 text-xs text-muted-foreground">
                    {t("hub.review.forbidden_notice")}
                  </p>
                ) : null}
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
