import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateSwipeDialog from "../components/create-swipe/create-swipe-dialog";
import ShowSwipeDialog from "../components/show-edit-or-delete-swipe/show-swipe-dialog";
import { SwipeDataTableRender } from "../components/swipe-data/swipe-data-table";

export default function SwipeList() {
  const { t } = useTranslation();
  const { canViewSwipes } = usePermissions();

  if (!canViewSwipes) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Swipes"
        description="Gestion de swipes"
      />
      <SwipeDataTableRender />
      <CreateSwipeDialog />
      <ShowSwipeDialog />
    </>
  );
}