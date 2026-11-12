import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateCompanyDialog from "../components/create-company/create-company-dialog";
import ShowCompanyDialog from "../components/show-edit-or-delete-company/show-company-dialog";
import { CompanyDataTableRender } from "../components/company-data/company-data-table";

export default function CompanyList() {
  const { t } = useTranslation();
  const { canViewCompanies } = usePermissions();

  if (!canViewCompanies) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Companies"
        description="Gestion de companies"
      />
      <CompanyDataTableRender />
      <CreateCompanyDialog />
      <ShowCompanyDialog />
    </>
  );
}