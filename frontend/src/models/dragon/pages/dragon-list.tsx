import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateDragonDialog from "../components/create-dragon/create-dragon-dialog";
import ShowDragonDialog from "../components/show-edit-or-delete-dragon/show-dragon-dialog";
import { DragonDataTableRender } from "../components/dragon-data/dragon-data-table";

export default function DragonList() {
  const { t } = useTranslation();
  const { canViewDragons } = usePermissions();

  if (!canViewDragons) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Dragons"
        description="Gestion de dragons"
      />
      <DragonDataTableRender />
      <CreateDragonDialog />
      <ShowDragonDialog />
    </>
  );
}