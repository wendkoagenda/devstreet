import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateGadoDialog from "../components/create-gado/create-gado-dialog";
import ShowGadoDialog from "../components/show-edit-or-delete-gado/show-gado-dialog";
import { GadoDataTableRender } from "../components/gado-data/gado-data-table";

export default function GadoList() {
  const { t } = useTranslation();
  const { canViewGados } = usePermissions();

  if (!canViewGados) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Gados"
        description="Gestion de gados"
      />
      <GadoDataTableRender />
      <CreateGadoDialog />
      <ShowGadoDialog />
    </>
  );
}