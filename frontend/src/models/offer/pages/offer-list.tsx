import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateOfferDialog from "../components/create-offer/create-offer-dialog";
import ShowOfferDialog from "../components/show-edit-or-delete-offer/show-offer-dialog";
import { OfferDataTableRender } from "../components/offer-data/offer-data-table";

export default function OfferList() {
  const { t } = useTranslation();
  const { canViewOffers } = usePermissions();

  if (!canViewOffers) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Offers"
        description="Gestion de offers"
      />
      <OfferDataTableRender />
      <CreateOfferDialog />
      <ShowOfferDialog />
    </>
  );
}