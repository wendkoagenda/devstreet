import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateConnectionDialog from "../components/create-connection/create-connection-dialog";
import ShowConnectionDialog from "../components/show-edit-or-delete-connection/show-connection-dialog";
import { ConnectionDataTableRender } from "../components/connection-data/connection-data-table";

export default function ConnectionList() {
  const { t } = useTranslation();
  const { canViewConnections } = usePermissions();

  if (!canViewConnections) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Connections"
        description="Gestion de connections"
      />
      <ConnectionDataTableRender />
      <CreateConnectionDialog />
      <ShowConnectionDialog />
    </>
  );
}