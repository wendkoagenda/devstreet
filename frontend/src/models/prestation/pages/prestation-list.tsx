import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreatePrestationDialog from "../components/create-prestation/create-prestation-dialog";
import ShowPrestationDialog from "../components/show-edit-or-delete-prestation/show-prestation-dialog";
import { PrestationDataTableRender } from "../components/prestation-data/prestation-data-table";

export default function PrestationList() {
  const { t } = useTranslation();
  const { canViewPrestations } = usePermissions();

  if (!canViewPrestations) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Prestations"
        description="Gestion de prestations"
      />
      <PrestationDataTableRender />
      <CreatePrestationDialog />
      <ShowPrestationDialog />
    </>
  );
}