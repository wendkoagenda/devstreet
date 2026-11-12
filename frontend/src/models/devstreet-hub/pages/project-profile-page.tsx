import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AlertTriangle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProjectProfileSections } from "../components/project-profile-sections";
import { useProjectProfile } from "../hooks/use-project-profile";

export default function ProjectProfilePage() {
  const { t } = useTranslation();
  const params = useParams();
  const userId = Number(params.userId);
  const profile = useProjectProfile(userId);

  if (!Number.isFinite(userId) || userId <= 0) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center text-sm text-muted-foreground">
        {t("hub.profile.errors.not_found")}
      </div>
    );
  }

  if (profile.isLoading && !profile.profile && profile.section === "overview") {
    return (
      <div className="mx-auto max-w-3xl py-16 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </div>
    );
  }

  if (profile.isError && profile.section === "overview" && !profile.profile) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">
          {profile.errorStatus === 403
            ? t("hub.profile.errors.forbidden")
            : t("hub.profile.errors.not_found")}
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

  const overviewProjects = profile.profile?.projects ?? [];
  const overviewContributions = profile.profile?.contributions ?? [];
  const limit = profile.profile?.limit ?? 20;

  const projects =
    profile.section === "projects"
      ? (profile.projectsPage?.results ?? [])
      : overviewProjects;
  const contributions =
    profile.section === "contributions"
      ? (profile.contributionsPage?.results ?? [])
      : overviewContributions;

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" className="h-8 gap-1.5 px-2 text-xs">
          <Link to="/hub/projects">
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.profile.back_explore")}
          </Link>
        </Button>
        <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
          {t("hub.profile.title", {
            name:
              profile.displayName ||
              t("hub.profile.user_fallback", { id: userId }),
          })}
        </h1>
      </div>

      <p className="max-w-3xl text-sm text-muted-foreground">
        {t("hub.profile.description")}
      </p>

      {profile.isError && profile.section !== "overview" ? (
        <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
          {profile.errorDetail || t("hub.profile.errors.list")}
        </p>
      ) : null}

      <ProjectProfileSections
        userId={userId}
        displayName={profile.displayName}
        section={profile.section}
        page={profile.page}
        pageSize={profile.pageSize}
        limit={limit}
        projects={projects}
        contributions={contributions}
        projectsCount={profile.projectsPage?.count}
        contributionsCount={profile.contributionsPage?.count}
        projectById={profile.projectById}
        onSectionChange={profile.setSection}
        onPageChange={profile.setPage}
      />
    </div>
  );
}
