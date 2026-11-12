import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateProfilDialog from "../components/create-profil/create-profil-dialog";
import ShowProfilDialog from "../components/show-edit-or-delete-profil/show-profil-dialog";
import { ProfilDataTableRender } from "../components/profil-data/profil-data-table";

export default function ProfilList() {
  const { t } = useTranslation();
  const { canViewProfils } = usePermissions();

  if (!canViewProfils) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Profils"
        description="Gestion de profils"
      />
      <ProfilDataTableRender />
      <CreateProfilDialog />
      <ShowProfilDialog />
    </>
  );
}