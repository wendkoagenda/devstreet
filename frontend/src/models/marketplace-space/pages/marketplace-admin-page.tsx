import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { usePermissions } from "@/hooks/use-permissions";
import { MARKETPLACE_ADMIN_PAGES } from "../admin-pages";

/** Administration de la marketplace : accès aux listes CRUD des 13 modèles, selon les permissions. */
export default function MarketplaceAdminPage() {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const pages = MARKETPLACE_ADMIN_PAGES.filter(
    (page) => permissions[page.permission]
  );

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold text-foreground">
          {t("marketplace.admin.title")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t("marketplace.admin.subtitle")}
        </p>
      </div>

      {pages.length === 0 ? (
        <p className="rounded-lg border border-dashed border-input bg-card p-6 text-sm text-muted-foreground">
          {t("marketplace.admin.empty")}
        </p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {pages.map((page) => (
            <Link key={page.path} to={page.path} className="group">
              <Card className="h-full transition-colors group-hover:bg-muted">
                <CardHeader className="flex-row items-center justify-between gap-2 space-y-0">
                  <div className="flex flex-col gap-1">
                    <CardTitle className="text-sm">{t(page.titleKey)}</CardTitle>
                    <CardDescription className="text-xs">
                      {t(page.descriptionKey)}
                    </CardDescription>
                  </div>
                  <ChevronRight className="size-4 shrink-0 text-muted-foreground" />
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
