import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateExperienceDialog from "../components/create-experience/create-experience-dialog";
import ShowExperienceDialog from "../components/show-edit-or-delete-experience/show-experience-dialog";
import { ExperienceDataTableRender } from "../components/experience-data/experience-data-table";

export default function ExperienceList() {
  const { t } = useTranslation();
  const { canViewExperiences } = usePermissions();

  if (!canViewExperiences) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Experiences"
        description="Gestion de experiences"
      />
      <ExperienceDataTableRender />
      <CreateExperienceDialog />
      <ShowExperienceDialog />
    </>
  );
}