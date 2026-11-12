import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateFusionDialog from "../components/create-fusion/create-fusion-dialog";
import ShowFusionDialog from "../components/show-edit-or-delete-fusion/show-fusion-dialog";
import { FusionDataTableRender } from "../components/fusion-data/fusion-data-table";

export default function FusionList() {
  const { t } = useTranslation();
  const { canViewFusions } = usePermissions();

  if (!canViewFusions) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Fusions"
        description="Gestion de fusions"
      />
      <FusionDataTableRender />
      <CreateFusionDialog />
      <ShowFusionDialog />
    </>
  );
}