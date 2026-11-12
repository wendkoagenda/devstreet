import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function PageTitleDisplayer({
  title,
  description,
  backButton = true,
  navigateTo,
}: {
  title: string;
  description: string;
  backButton?: boolean;
  navigateTo?: string;
}) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleBack = () => {
    if (navigateTo) {
      navigate(navigateTo);
    } else {
      navigate(-1);
    }
  };

  return (
    <div className="mb-8">
      <div className="flex items-center gap-4 mb-2">
        {backButton && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleBack}
            className="h-8 w-8"
            title={t("common.back")}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        )}
        <h1 className="text-2xl font-bold">{title}</h1>
      </div>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
