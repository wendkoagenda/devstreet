import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateUserDialog from "../components/create-user/create-user-dialog";
import ShowUserDialog from "../components/show-edit-or-delete-user/show-user-dialog";
import { UserDataTableRender } from "../components/user-data/user-data-table";

export default function UsersList() {
  const { t } = useTranslation();

  const { canViewUsers } = usePermissions();
  if (!canViewUsers) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title={t("users.name")}
        description={t("users.description")}
      />
      <UserDataTableRender />
      <CreateUserDialog />
      <ShowUserDialog />
    </>
  );
}
