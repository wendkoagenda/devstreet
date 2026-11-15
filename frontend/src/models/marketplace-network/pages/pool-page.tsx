import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate } from "@/models/marketplace-offers/labels";
import { PoolStatsStrip } from "@/models/marketplace-stats/components/page-stats";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useGetPoolQuery } from "../api";

function PoolContent() {
  const { t } = useTranslation();
  const { data, isLoading, isError } = useGetPoolQuery();

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4">
      <PoolStatsStrip />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">{t("marketplace.pool_title")}</h1>
          <p className="text-sm text-muted-foreground">{t("marketplace.pool_sub")}</p>
        </div>
        <Button asChild variant="outline">
          <Link to="/marketplace/talents">{t("marketplace.talents_directory")}</Link>
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-40 w-full" />
      ) : isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          {t("marketplace.load_pool_error")}
        </p>
      ) : data && data.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((talent) => (
            <Card key={talent.id}>
              <CardContent className="flex flex-col gap-3 p-4">
                <div className="flex items-center gap-3">
                  <ProfileInitialsAvatar name={talent.name} openToWork={talent.is_open_to_work} />
                  <span className="flex min-w-0 flex-col">
                    <span className="truncate text-sm font-semibold text-foreground">
                      {talent.name}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {[talent.headline, talent.city].filter(Boolean).join(" · ")}
                    </span>
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {talent.skills.slice(0, 4).map((skill) => (
                    <Badge key={skill} variant="outline">
                      {skill}
                    </Badge>
                  ))}
                </div>
                <span className="text-xs text-muted-foreground">
                  {t("marketplace.pool_kept_by", {
                    name: talent.liked_by,
                    date: formatDate(talent.liked_at),
                  })}
                </span>
                <div className="flex gap-2">
                  <Button asChild size="sm" className="flex-1">
                    <Link to={`/marketplace/profiles/${talent.id}`}>
                      {t("marketplace.view_profile")}
                    </Link>
                  </Button>
                  {talent.email ? (
                    <Button asChild size="sm" variant="outline">
                      <a href={`mailto:${talent.email}`}>{t("marketplace.contact")}</a>
                    </Button>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
          {t("marketplace.pool_empty")}
          <Button asChild>
            <Link to="/marketplace/talents">{t("marketplace.talents_directory")}</Link>
          </Button>
        </div>
      )}
    </div>
  );
}

/** Vivier de talents de l'entreprise (profils likés en contexte recrutement). */
export default function PoolPage() {
  return (
    <RequireRecruiter>
      <PoolContent />
    </RequireRecruiter>
  );
}
