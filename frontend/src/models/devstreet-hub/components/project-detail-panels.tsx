import { Pencil, Plus, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { pageCountOf, PAGE_SIZE } from "@/helpers/api/pagination";
import { useUpdateProjectMutation } from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type {
  ContributionTask,
  Project,
  ProjectMember,
  ProjectMemberWrite,
  TaskWrite,
} from "../schema";
import type { Paginated } from "@/helpers/api/pagination";
import { CodeBrowser } from "./code-browser";

interface PresentationPanelProps {
  project: Project;
  canEdit: boolean;
}

export function PresentationPanel({ project, canEdit }: PresentationPanelProps) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [problem, setProblem] = useState(project.problem);
  const [description, setDescription] = useState(project.description);
  const [updateProject, updateState] = useUpdateProjectMutation();

  useEffect(() => {
    if (!editing) {
      setProblem(project.problem);
      setDescription(project.description);
    }
  }, [editing, project.description, project.problem]);

  const handleSave = async () => {
    try {
      await updateProject({
        projectId: project.id,
        body: {
          problem: problem.trim(),
          description: description.trim(),
        },
      }).unwrap();
      toast.success(t("hub.detail.toasts.presentation_saved"));
      setEditing(false);
    } catch (error) {
      const detail = apiDetailOf(error);
      const status = httpStatusOf(error);
      toast.error(
        detail ||
          (status === 403
            ? t("hub.detail.errors.forbidden")
            : t("hub.detail.errors.presentation_save"))
      );
    }
  };

  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-card sm:p-6">
      <div className="mb-3 flex items-start justify-between gap-3">
        <h2 className="text-sm font-bold text-foreground">
          {t("hub.detail.presentation.title")}
        </h2>
        {canEdit && !editing ? (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8 shrink-0 text-muted-foreground hover:text-foreground"
            aria-label={t("hub.detail.presentation.edit")}
            onClick={() => setEditing(true)}
          >
            <Pencil aria-hidden className="size-3.5" />
          </Button>
        ) : null}
      </div>

      {editing ? (
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="presentation-problem">
              {t("hub.detail.presentation.problem_label")}
            </Label>
            <Textarea
              id="presentation-problem"
              value={problem}
              onChange={(event) => setProblem(event.target.value)}
              rows={3}
              maxLength={2000}
              className="min-h-[5rem] resize-y text-sm"
              placeholder={t("hub.detail.presentation.problem_placeholder")}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="presentation-description">
              {t("hub.detail.presentation.description_label")}
            </Label>
            <Textarea
              id="presentation-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={8}
              maxLength={10000}
              className="min-h-[10rem] resize-y text-sm"
              placeholder={t("hub.detail.presentation.description_placeholder")}
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              className="h-9 text-xs font-semibold"
              disabled={updateState.isLoading}
              onClick={() => void handleSave()}
            >
              {updateState.isLoading
                ? t("hub.detail.presentation.saving")
                : t("hub.detail.presentation.save")}
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="h-9 text-xs"
              disabled={updateState.isLoading}
              onClick={() => {
                setProblem(project.problem);
                setDescription(project.description);
                setEditing(false);
              }}
            >
              {t("common.cancel")}
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          <div>
            <p className="mb-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
              {t("hub.detail.presentation.problem_label")}
            </p>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
              {project.problem.trim() || t("hub.detail.presentation.problem_empty")}
            </p>
          </div>
          <div>
            <p className="mb-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
              {t("hub.detail.presentation.description_label")}
            </p>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
              {project.description.trim() || t("hub.detail.presentation.empty")}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}

interface CodePanelProps {
  projectId: number;
  projectTitle: string;
  isOwner: boolean;
  repositoryReady: boolean;
  namespace?: string | null;
  repoName?: string | null;
}

export function CodePanel({
  projectId,
  projectTitle,
  isOwner,
  repositoryReady,
  namespace,
  repoName,
}: CodePanelProps) {
  const { t } = useTranslation();

  if (!repositoryReady) {
    return (
      <section className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-card sm:p-6">
        <h2 className="text-sm font-bold text-foreground">{t("hub.detail.code.title")}</h2>
        <p className="rounded-lg border border-dashed border-border bg-secondary/60 px-3 py-3 text-xs text-muted-foreground">
          {t("hub.detail.code.not_ready")}
        </p>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-3">
      <CodeBrowser
        projectId={projectId}
        projectTitle={projectTitle}
        isOwner={isOwner}
        namespaceHint={namespace}
        repoNameHint={repoName}
      />
    </section>
  );
}

interface ContributePanelProps {
  projectId: number;
  tasks: Paginated<ContributionTask> | undefined;
  loading: boolean;
  page: number;
  onPageChange: (page: number) => void;
  canCreateTask: boolean;
  onOpenCreateTask: () => void;
}

export function ContributePanel({
  projectId,
  tasks,
  loading,
  page,
  onPageChange,
  canCreateTask,
  onOpenCreateTask,
}: ContributePanelProps) {
  const { t } = useTranslation();
  const pageCount = pageCountOf(tasks?.count ?? 0, PAGE_SIZE);

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-bold text-foreground">
          {t("hub.detail.contribute.title")}
        </h2>
        {canCreateTask ? (
          <Button
            type="button"
            variant="outline"
            onClick={onOpenCreateTask}
            className="h-8 gap-1.5 rounded-lg text-xs font-semibold"
          >
            <Plus aria-hidden className="size-3.5" />
            {t("hub.detail.actions.create_task")}
          </Button>
        ) : null}
      </div>

      {loading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : !tasks || tasks.results.length === 0 ? (
        <p className="rounded-xl border border-dashed border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground">
          {t("hub.detail.contribute.empty")}
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {tasks.results.map((task) => (
            <li
              key={task.id}
              className="rounded-xl border border-border bg-card p-4 shadow-card"
            >
              <div className="mb-1.5 flex flex-wrap items-center gap-2">
                <span className="rounded bg-secondary px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                  {t(`hub.detail.task_status.${task.status}`)}
                </span>
                <h3 className="text-sm font-bold text-foreground">{task.title}</h3>
              </div>
              <p className="mb-3 line-clamp-2 text-xs text-muted-foreground">
                {task.description || t("hub.detail.contribute.no_description")}
              </p>
              <Button asChild variant="outline" className="h-8 rounded-lg text-xs font-semibold">
                <Link to={`/hub/projects/${projectId}/tasks/${task.id}`}>
                  {t("hub.detail.contribute.open_task")}
                </Link>
              </Button>
            </li>
          ))}
        </ul>
      )}

      {pageCount > 1 ? (
        <div className="flex items-center justify-between gap-2 text-xs">
          <Button
            type="button"
            variant="outline"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="h-8 rounded-lg"
          >
            {t("pagination.previous")}
          </Button>
          <span className="text-muted-foreground">
            {t("hub.detail.page_of", { page, pageCount })}
          </span>
          <Button
            type="button"
            variant="outline"
            disabled={page >= pageCount}
            onClick={() => onPageChange(page + 1)}
            className="h-8 rounded-lg"
          >
            {t("pagination.next")}
          </Button>
        </div>
      ) : null}
    </section>
  );
}

interface TeamPanelProps {
  project: Project;
  members: Paginated<ProjectMember> | undefined;
  loading: boolean;
  page: number;
  onPageChange: (page: number) => void;
  canManage: boolean;
  isBusy: boolean;
  onInvite: (body: ProjectMemberWrite) => Promise<boolean>;
  onRemove: (userId: number) => void;
}

export function TeamPanel({
  project,
  members,
  loading,
  page,
  onPageChange,
  canManage,
  isBusy,
  onInvite,
  onRemove,
}: TeamPanelProps) {
  const { t } = useTranslation();
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState<"maintainer" | "contributor">("contributor");
  const pageCount = pageCountOf(members?.count ?? 0, PAGE_SIZE);

  const handleInvite = async () => {
    const id = Number(userId);
    if (!Number.isFinite(id) || id <= 0) return;
    const ok = await onInvite({ user_id: id, role });
    if (ok) setUserId("");
  };

  return (
    <section className="flex flex-col gap-4">
      <h2 className="text-sm font-bold text-foreground">{t("hub.detail.team.title")}</h2>
      <p className="text-xs text-muted-foreground">{t("hub.detail.team.hint")}</p>

      <div className="rounded-xl border border-border bg-card p-4 text-xs shadow-card">
        <span className="font-semibold text-foreground">
          {t("hub.detail.team.owner", { id: project.owner_id })}
        </span>
      </div>

      {canManage ? (
        <div className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4 shadow-card sm:flex-row sm:items-end">
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="member-user-id">{t("hub.detail.team.user_id")}</Label>
            <Input
              id="member-user-id"
              type="number"
              min={1}
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              className="h-9 bg-secondary"
              placeholder="42"
            />
          </div>
          <div className="flex w-full flex-col gap-1.5 sm:w-40">
            <Label>{t("hub.detail.team.role")}</Label>
            <Select
              value={role}
              onValueChange={(value) =>
                setRole(value as "maintainer" | "contributor")
              }
            >
              <SelectTrigger className="h-9 rounded-lg bg-secondary text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="contributor">
                  {t("hub.detail.team.roles.contributor")}
                </SelectItem>
                <SelectItem value="maintainer">
                  {t("hub.detail.team.roles.maintainer")}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button
            type="button"
            disabled={isBusy || !userId}
            onClick={() => {
              void handleInvite();
            }}
            className="h-9 rounded-lg text-xs font-semibold"
          >
            {t("hub.detail.team.invite")}
          </Button>
        </div>
      ) : null}

      {loading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : !members || members.results.length === 0 ? (
        <p className="rounded-xl border border-dashed border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground">
          {t("hub.detail.team.empty")}
        </p>
      ) : (
        <ul className="flex flex-col gap-2">
          {members.results.map((member) => (
            <li
              key={member.id}
              className="flex items-center justify-between gap-3 rounded-xl border border-border bg-card px-4 py-3 text-xs shadow-card"
            >
              <div>
                <span className="font-semibold text-foreground">
                  {t("hub.detail.team.user", { id: member.user_id })}
                </span>
                <span className="ml-2 text-muted-foreground">
                  {t(`hub.detail.team.roles.${member.role}`)}
                </span>
              </div>
              {canManage ? (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  disabled={isBusy}
                  className="h-8 w-8 text-destructive"
                  aria-label={t("hub.detail.team.remove")}
                  onClick={() => onRemove(member.user_id)}
                >
                  <Trash2 aria-hidden className="size-3.5" />
                </Button>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {pageCount > 1 ? (
        <div className="flex items-center justify-between gap-2 text-xs">
          <Button
            type="button"
            variant="outline"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="h-8 rounded-lg"
          >
            {t("pagination.previous")}
          </Button>
          <span className="text-muted-foreground">
            {t("hub.detail.page_of", { page, pageCount })}
          </span>
          <Button
            type="button"
            variant="outline"
            disabled={page >= pageCount}
            onClick={() => onPageChange(page + 1)}
            className="h-8 rounded-lg"
          >
            {t("pagination.next")}
          </Button>
        </div>
      ) : null}
    </section>
  );
}

interface CreateTaskFormProps {
  isBusy: boolean;
  onSubmit: (body: TaskWrite) => Promise<boolean>;
  onCancel: () => void;
}

export function CreateTaskForm({ isBusy, onSubmit, onCancel }: CreateTaskFormProps) {
  const { t } = useTranslation();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  return (
    <form
      className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4 shadow-card"
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit({ title: title.trim(), description: description.trim() }).then(
          (ok) => {
            if (ok) {
              setTitle("");
              setDescription("");
            }
          }
        );
      }}
    >
      <h3 className="text-sm font-bold text-foreground">
        {t("hub.detail.task_form.title")}
      </h3>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="task-title">{t("hub.detail.task_form.name")}</Label>
        <Input
          id="task-title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className="h-9 bg-secondary"
          required
          maxLength={180}
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="task-description">{t("hub.detail.task_form.description")}</Label>
        <Textarea
          id="task-description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="min-h-[80px] bg-secondary text-xs"
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel} className="h-8 text-xs">
          {t("common.cancel")}
        </Button>
        <Button type="submit" disabled={isBusy || !title.trim()} className="h-8 text-xs">
          {t("hub.detail.task_form.submit")}
        </Button>
      </div>
    </form>
  );
}
