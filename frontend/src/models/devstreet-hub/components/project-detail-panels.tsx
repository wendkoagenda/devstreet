import { Pencil } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useUpdateProjectMutation } from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type { Project } from "../schema";
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
