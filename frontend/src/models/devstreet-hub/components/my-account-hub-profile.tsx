import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProjectProfileSections } from "./project-profile-sections";
import { useProjectProfile } from "../hooks/use-project-profile";

interface MyAccountHubProfileProps {
  userId: number;
}

/**
 * Extension Hub du profil commun : réalisations sans dupliquer l'identité IAM.
 */
export function MyAccountHubProfile({ userId }: MyAccountHubProfileProps) {
  const { t } = useTranslation();
  const profile = useProjectProfile(userId);

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
    <section className="mt-8 flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            {t("hub.profile.account_section_title")}
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            {t("hub.profile.account_section_hint")}
          </p>
        </div>
        <Button asChild variant="outline" className="h-8 gap-1.5 text-xs">
          <Link to={`/hub/profiles/${userId}`}>
            <ExternalLink aria-hidden className="size-3.5" />
            {t("hub.profile.open_public")}
          </Link>
        </Button>
      </div>

      {profile.isLoading && !profile.profile ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : profile.isError && !profile.profile ? (
        <p className="text-sm text-destructive">
          {t("hub.profile.errors.not_found")}
        </p>
      ) : (
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
      )}
    </section>
  );
}
