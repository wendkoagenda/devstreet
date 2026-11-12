import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateProfilSkillDialog from "../components/create-profil-skill/create-profil-skill-dialog";
import ShowProfilSkillDialog from "../components/show-edit-or-delete-profil-skill/show-profil-skill-dialog";
import { ProfilSkillDataTableRender } from "../components/profil-skill-data/profil-skill-data-table";

export default function ProfilSkillList() {
  const { t } = useTranslation();
  const { canViewProfilSkills } = usePermissions();

  if (!canViewProfilSkills) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Profil-skills"
        description="Gestion de profil-skills"
      />
      <ProfilSkillDataTableRender />
      <CreateProfilSkillDialog />
      <ShowProfilSkillDialog />
    </>
  );
}