import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateAvailabilityDialog from "../components/create-availability/create-availability-dialog";
import ShowAvailabilityDialog from "../components/show-edit-or-delete-availability/show-availability-dialog";
import { AvailabilityDataTableRender } from "../components/availability-data/availability-data-table";

export default function AvailabilityList() {
  const { t } = useTranslation();
  const { canViewAvailabilities } = usePermissions();

  if (!canViewAvailabilities) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Availabilities"
        description="Gestion de availabilities"
      />
      <AvailabilityDataTableRender />
      <CreateAvailabilityDialog />
      <ShowAvailabilityDialog />
    </>
  );
}