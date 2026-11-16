import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  FeedComposer,
  type ComposerMode,
  type FeedComposerDefaultValues,
} from "@/models/forum/components/feed-composer";
import type { Project, Technology } from "../schema";

const HUB_SHARE_MODES: ComposerMode[] = [
  "APPLICATION",
  "DISCUSSION",
  "ENTRAIDE",
];

type ProjectShareForumDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  project: Project;
  technologies: Technology[];
  initialMode: ComposerMode;
};

function buildDefaults(
  project: Project,
  technologies: Technology[],
  mode: ComposerMode
): FeedComposerDefaultValues {
  const body =
    [project.problem?.trim(), project.description?.trim()]
      .filter(Boolean)
      .join("\n\n") || project.title;
  const tags = technologies
    .map((tech) => tech.label || tech.slug)
    .filter(Boolean)
    .slice(0, 3);
  const images =
    project.images
      ?.filter((img) => img.url?.trim())
      .slice(0, 10)
      .map((img, position) => ({
        url: img.url,
        kind: "IMAGE" as const,
        texte_alternatif: img.display_name || project.title,
        position,
      })) ?? [];

  return {
    titre: project.title,
    description: body,
    tags_data: tags,
    images_data: images,
    ...(mode === "APPLICATION"
      ? {
          lien_app: project.demo_url?.trim() || "",
          plateforme_app: "WEB" as const,
        }
      : {}),
  };
}

export function ProjectShareForumDialog({
  open,
  onOpenChange,
  project,
  technologies,
  initialMode,
}: ProjectShareForumDialogProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const defaults = useMemo(
    () => buildDefaults(project, technologies, initialMode),
    [project, technologies, initialMode]
  );

  const titleKey =
    initialMode === "APPLICATION"
      ? "hub.detail.share_forum.dialog_title_application"
      : initialMode === "ENTRAIDE"
        ? "hub.detail.share_forum.dialog_title_entraide"
        : "hub.detail.share_forum.dialog_title_discussion";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t(titleKey)}</DialogTitle>
        </DialogHeader>
        {open ? (
          <FeedComposer
            key={`${project.id}-${initialMode}`}
            bare
            forceExpanded
            linkedProjectId={project.id}
            initialMode={initialMode}
            allowedModes={HUB_SHARE_MODES}
            defaultValues={defaults}
            onCancel={() => onOpenChange(false)}
            onCreated={(publicationId) => {
              onOpenChange(false);
              toast.success(t("hub.detail.share_forum.toast_success"), {
                action: {
                  label: t("hub.detail.share_forum.open_forum"),
                  onClick: () =>
                    navigate(`/forum/publications/${publicationId}`),
                },
              });
            }}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
