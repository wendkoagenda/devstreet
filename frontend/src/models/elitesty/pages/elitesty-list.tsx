import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateElitestyDialog from "../components/create-elitesty/create-elitesty-dialog";
import ShowElitestyDialog from "../components/show-edit-or-delete-elitesty/show-elitesty-dialog";
import { ElitestyDataTableRender } from "../components/elitesty-data/elitesty-data-table";

export default function ElitestyList() {
  const { t } = useTranslation();
  const { canViewElitesties } = usePermissions();

  if (!canViewElitesties) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Elitesties"
        description="Gestion de elitesties"
      />
      <ElitestyDataTableRender />
      <CreateElitestyDialog />
      <ShowElitestyDialog />
    </>
  );
}