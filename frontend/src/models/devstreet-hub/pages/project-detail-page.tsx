import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AlertTriangle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ComposerMode } from "@/models/forum/components/feed-composer";
import { HubAssistantPanel } from "@/models/ai/components/hub-assistant-panel";
import { useLazyListProjectForumPostsQuery } from "../api";
import { ProjectDetailHeader } from "../components/project-detail-header";
import {
  CodePanel,
  PresentationPanel,
} from "../components/project-detail-panels";
import { ContributeTasksPanel } from "../components/contribute-tasks-panel";
import { CreateTaskForm } from "../components/create-task-form";
import { HubConfirmDialog } from "../components/hub-confirm-dialog";
import { ProjectShareForumDialog } from "../components/project-share-forum-dialog";
import { ProjectDetailTabs } from "../components/project-detail-tabs";
import { TeamPanel } from "../components/team-panel";
import { resolveShareForumIntent } from "../functions/resolve-share-forum-intent";
import { useProjectDetail } from "../hooks/use-project-detail";

type ConfirmAction =
  | { type: "publish" }
  | { type: "archive" }
  | { type: "remove_member"; userId: number };

export default function ProjectDetailPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const params = useParams();
  const projectId = Number(params.id);
  const detail = useProjectDetail(projectId);
  const [listForumPosts] = useLazyListProjectForumPostsQuery();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [shareMode, setShareMode] = useState<ComposerMode | null>(null);
  const [confirmAction, setConfirmAction] = useState<ConfirmAction | null>(
    null
  );
  const repositoryReady = detail.repository?.status === "ready";

  if (!Number.isFinite(projectId) || projectId <= 0) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center">
        <p className="mb-4 text-sm text-muted-foreground">{t("hub.detail.errors.not_found")}</p>
        <Button asChild variant="outline" className="h-9 text-xs">
          <Link to="/hub/projects">{t("hub.upcoming.back")}</Link>
        </Button>
      </div>
    );
  }

  if (detail.isLoading && !detail.project) {
    return (
      <div className="mx-auto max-w-3xl py-16 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </div>
    );
  }

  if (detail.isError || !detail.project || !detail.star) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">
          {detail.errorStatus === 403
            ? t("hub.detail.errors.forbidden")
            : t("hub.detail.errors.not_found")}
        </p>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            className="h-9 text-xs"
            onClick={() => void detail.refetch()}
          >
            {t("hub.common.retry")}
          </Button>
          <Button asChild variant="outline" className="h-9 text-xs">
            <Link to="/hub/projects">
              <ArrowLeft aria-hidden className="mr-1 size-3.5" />
              {t("hub.upcoming.back")}
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  const project = detail.project;
  const repository = detail.repository;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <ProjectDetailHeader
        technologies={project.technologies.flatMap(id => { const tech = detail.technologiesById.get(id); return tech ? [tech] : []; })}
        project={project}
        star={detail.star}
        isOwner={detail.isOwner}
        canPublish={detail.isOwner && detail.access.canPublishProject}
        canArchive={detail.isOwner && detail.access.canArchiveProject}
        canCreateTask={detail.access.canCreateTask}
        canAnalyze={detail.isOwner && detail.access.canAnalyze}
        canReview={detail.isOwner && detail.access.canReviewContributions}
        canShareForum={
          detail.access.isAuthenticated && detail.access.canDiscuss
        }
        isBusy={detail.isBusy}
        onToggleStar={() => {
          void detail.toggleStar();
        }}
        onPublish={() => setConfirmAction({ type: "publish" })}
        onArchive={() => setConfirmAction({ type: "archive" })}
        onCreateTask={() => {
          detail.setTab("contribute");
          setShowTaskForm(true);
        }}
        onShareForum={(kind) => {
          void (async () => {
            if (!detail.access.isAuthenticated) {
              detail.access.requestLogin();
              return;
            }
            const resolved = await resolveShareForumIntent({
              kind,
              projectId: project.id,
              demoUrl: project.demo_url,
              listForumPosts,
              t,
              navigate,
            });
            if (resolved) setShareMode(resolved);
          })();
        }}
      />

      {shareMode ? (
        <ProjectShareForumDialog
          open
          onOpenChange={(open) => {
            if (!open) setShareMode(null);
          }}
          project={project}
          technologies={project.technologies.flatMap((id) => {
            const tech = detail.technologiesById.get(id);
            return tech ? [tech] : [];
          })}
          initialMode={shareMode}
        />
      ) : null}

      <ProjectDetailTabs active={detail.tab} onChange={detail.setTab} />

      {detail.tab === "presentation" ? (
        <PresentationPanel
          key={project.id}
          canAnalyze={detail.access.canAnalyze}
          onNavigate={detail.setTab}
          technologies={project.technologies.flatMap(id => { const tech = detail.technologiesById.get(id); return tech ? [tech] : []; })}
          project={project}
          canEdit={detail.isOwner && detail.access.canUpdateProject}
        />
      ) : null}

      {detail.tab === "code" ? (
        <CodePanel
          projectId={project.id}
          projectTitle={project.title}
          isOwner={detail.isOwner}
          repositoryReady={Boolean(repositoryReady)}
          namespace={repository?.namespace}
          repoName={repository?.name}
        />
      ) : null}

      {detail.tab === "contribute" ? (
        showTaskForm ? (
          <CreateTaskForm
            isBusy={detail.isBusy}
            onCancel={() => setShowTaskForm(false)}
            onSubmit={async (body) => {
              const ok = await detail.createManualTask(body);
              if (ok) {
                setShowTaskForm(false);
                detail.setTasksStatus("draft");
              }
              return ok;
            }}
          />
        ) : (
          <ContributeTasksPanel
            projectId={project.id}
            tasks={detail.tasks}
            loading={detail.tasksLoading}
            page={detail.tasksPage}
            status={detail.tasksStatus}
            search={detail.tasksSearch}
            canCreateTask={detail.access.canCreateTask}
            canSeeDrafts={detail.isOwner || detail.access.canCreateTask}
            onPageChange={detail.setTasksPage}
            onStatusChange={detail.setTasksStatus}
            onSearchChange={detail.setTasksSearch}
            onOpenCreateTask={() => setShowTaskForm(true)}
          />
        )
      ) : null}

      {detail.tab === "team" ? (
        <TeamPanel
          project={project}
          members={detail.members}
          loading={detail.membersLoading}
          page={detail.membersPage}
          onPageChange={detail.setMembersPage}
          canManage={detail.isOwner && detail.access.canManageMembers}
          isBusy={detail.isBusy}
          onInvite={detail.inviteMember}
          onUpdateRole={detail.updateMemberRole}
          onRemove={(userId) =>
            setConfirmAction({ type: "remove_member", userId })
          }
        />
      ) : null}

      <HubAssistantPanel projectId={project.id} projectTitle={project.title} />

      <HubConfirmDialog
        open={confirmAction?.type === "publish"}
        title={t("hub.detail.actions.publish")}
        description={t("hub.detail.confirm.publish")}
        confirmLabel={t("hub.detail.actions.publish")}
        busy={detail.isBusy}
        onOpenChange={(open) => {
          if (!open) setConfirmAction(null);
        }}
        onConfirm={() => {
          void detail.publish().finally(() => setConfirmAction(null));
        }}
      />
      <HubConfirmDialog
        open={confirmAction?.type === "archive"}
        title={t("hub.detail.actions.archive")}
        description={t("hub.detail.confirm.archive")}
        confirmLabel={t("hub.detail.actions.archive")}
        destructive
        busy={detail.isBusy}
        onOpenChange={(open) => {
          if (!open) setConfirmAction(null);
        }}
        onConfirm={() => {
          void detail.archive().finally(() => setConfirmAction(null));
        }}
      />
      <HubConfirmDialog
        open={confirmAction?.type === "remove_member"}
        title={t("hub.detail.actions.manage")}
        description={t("hub.detail.confirm.remove_member")}
        confirmLabel={t("hub.detail.actions.remove_member")}
        destructive
        busy={detail.isBusy}
        onOpenChange={(open) => {
          if (!open) setConfirmAction(null);
        }}
        onConfirm={() => {
          if (confirmAction?.type !== "remove_member") return;
          void detail
            .ejectMember(confirmAction.userId)
            .finally(() => setConfirmAction(null));
        }}
      />
    </div>
  );
}
