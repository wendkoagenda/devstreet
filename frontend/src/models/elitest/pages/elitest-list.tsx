import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateElitestDialog from "../components/create-elitest/create-elitest-dialog";
import ShowElitestDialog from "../components/show-edit-or-delete-elitest/show-elitest-dialog";
import { ElitestDataTableRender } from "../components/elitest-data/elitest-data-table";

export default function ElitestList() {
  const { t } = useTranslation();
  const { canViewElitests } = usePermissions();

  if (!canViewElitests) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Elitests"
        description="Gestion de elitests"
      />
      <ElitestDataTableRender />
      <CreateElitestDialog />
      <ShowElitestDialog />
    </>
  );
}