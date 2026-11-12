import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateProfilHistoryDialog from "../components/create-profil-history/create-profil-history-dialog";
import ShowProfilHistoryDialog from "../components/show-edit-or-delete-profil-history/show-profil-history-dialog";
import { ProfilHistoryDataTableRender } from "../components/profil-history-data/profil-history-data-table";

export default function ProfilHistoryList() {
  const { t } = useTranslation();
  const { canViewProfilHistories } = usePermissions();

  if (!canViewProfilHistories) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Profil-histories"
        description="Gestion de profil-histories"
      />
      <ProfilHistoryDataTableRender />
      <CreateProfilHistoryDialog />
      <ShowProfilHistoryDialog />
    </>
  );
}