import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateSkillDialog from "../components/create-skill/create-skill-dialog";
import ShowSkillDialog from "../components/show-edit-or-delete-skill/show-skill-dialog";
import { SkillDataTableRender } from "../components/skill-data/skill-data-table";

export default function SkillList() {
  const { t } = useTranslation();
  const { canViewSkills } = usePermissions();

  if (!canViewSkills) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Skills"
        description="Gestion de skills"
      />
      <SkillDataTableRender />
      <CreateSkillDialog />
      <ShowSkillDialog />
    </>
  );
}