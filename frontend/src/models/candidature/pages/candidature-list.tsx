import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateCandidatureDialog from "../components/create-candidature/create-candidature-dialog";
import ShowCandidatureDialog from "../components/show-edit-or-delete-candidature/show-candidature-dialog";
import { CandidatureDataTableRender } from "../components/candidature-data/candidature-data-table";

export default function CandidatureList() {
  const { t } = useTranslation();
  const { canViewCandidatures } = usePermissions();

  if (!canViewCandidatures) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Candidatures"
        description="Gestion de candidatures"
      />
      <CandidatureDataTableRender />
      <CreateCandidatureDialog />
      <ShowCandidatureDialog />
    </>
  );
}