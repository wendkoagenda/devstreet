import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import CreateReviewDialog from "../components/create-review/create-review-dialog";
import ShowReviewDialog from "../components/show-edit-or-delete-review/show-review-dialog";
import { ReviewDataTableRender } from "../components/review-data/review-data-table";

export default function ReviewList() {
  const { t } = useTranslation();
  const { canViewReviews } = usePermissions();

  if (!canViewReviews) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <>
      <PageTitleDisplayer
        title="Reviews"
        description="Gestion de reviews"
      />
      <ReviewDataTableRender />
      <CreateReviewDialog />
      <ShowReviewDialog />
    </>
  );
}