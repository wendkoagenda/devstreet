import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Search, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { formatDate, initialsOf } from "@/models/marketplace-offers/labels";
import { useGetSkillOptionsQuery } from "@/models/marketplace-offers/api";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { COUNTRIES, countryName } from "@/models/marketplace-space/options";
import { useGetTalentsQuery } from "../api";
import type { TalentDirectoryCard } from "../schema";

function TalentRow({ talent }: { talent: TalentDirectoryCard }) {
  const { t } = useTranslation();
  const place = [talent.city, countryName(talent.country)].filter(Boolean).join(", ");
  return (
    <Link
      to={`/marketplace/profiles/${talent.id}`}
      className="flex items-start gap-3 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-muted/40"
    >
      <span
        className="flex size-11 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-sm font-semibold text-foreground"
        aria-hidden
      >
        {initialsOf(talent.name)}
      </span>
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold text-foreground">{talent.name}</span>
          {talent.remote ? <Badge variant="secondary">{t("marketplace.remote")}</Badge> : null}
          {talent.available_from ? (
            <Badge variant="outline">
              {t("marketplace.available_short", { date: formatDate(talent.available_from) })}
            </Badge>
          ) : null}
        </div>
        <span className="truncate text-xs text-muted-foreground">
          {[
            talent.headline,
            place,
            t("marketplace.years_short", { count: talent.years_of_experience }),
          ]
            .filter(Boolean)
            .join(" · ")}
        </span>
        {talent.skills.length > 0 ? (
          <div className="flex flex-wrap gap-1 pt-1">
            {talent.skills.slice(0, 5).map((skill) => (
              <Badge key={skill} variant="secondary">
                {skill}
              </Badge>
            ))}
          </div>
        ) : null}
      </div>
      {talent.rating_avg !== null ? (
        <span className="flex shrink-0 items-center gap-1 text-xs text-muted-foreground">
          <Star className="size-3.5" aria-hidden />
          {talent.rating_avg}
        </span>
      ) : null}
    </Link>
  );
}

function TalentsDirectoryContent() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [skill, setSkill] = useState("");
  const [country, setCountry] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [availableOnly, setAvailableOnly] = useState(false);
  const debouncedSearch = useDebouncedValue(search);
  const { data: skills } = useGetSkillOptionsQuery();
  const { data, isFetching, isError } = useGetTalentsQuery({
    search: debouncedSearch,
    skill,
    country,
    remote: remoteOnly ? "1" : "",
    available: availableOnly ? "1" : "",
  });

  const popularSkills = (skills ?? []).slice(0, 8);

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">
            {t("marketplace.talents_directory")}
          </h1>
          <p className="text-sm text-muted-foreground">
            {t("marketplace.talents_directory_sub")}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <Link to="/marketplace/talents/discover">{t("marketplace.swipe_mode")}</Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/marketplace/talents/pool">{t("marketplace.pool")}</Link>
          </Button>
        </div>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          className="pl-9"
          placeholder={t("marketplace.search_talent_placeholder")}
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label={t("marketplace.search_talent")}
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {popularSkills.map((option) => (
          <Button
            key={option.id}
            type="button"
            size="sm"
            variant={skill === String(option.id) ? "default" : "outline"}
            aria-pressed={skill === String(option.id)}
            onClick={() => setSkill(skill === String(option.id) ? "" : String(option.id))}
          >
            {option.name}
          </Button>
        ))}
        <Button
          type="button"
          size="sm"
          variant={remoteOnly ? "default" : "outline"}
          aria-pressed={remoteOnly}
          onClick={() => setRemoteOnly(!remoteOnly)}
        >
          {t("marketplace.remote")}
        </Button>
        <Button
          type="button"
          size="sm"
          variant={availableOnly ? "default" : "outline"}
          aria-pressed={availableOnly}
          onClick={() => setAvailableOnly(!availableOnly)}
        >
          {t("marketplace.available")}
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {COUNTRIES.slice(0, 10).map((item) => (
          <Button
            key={item.code}
            type="button"
            size="sm"
            variant={country === item.code ? "default" : "outline"}
            aria-pressed={country === item.code}
            onClick={() => setCountry(country === item.code ? "" : item.code)}
          >
            {item.name}
          </Button>
        ))}
      </div>

      {isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          {t("marketplace.load_directory_error")}
        </p>
      ) : isFetching && !data ? (
        <div className="flex flex-col gap-3">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      ) : data && data.length > 0 ? (
        <div className="flex flex-col gap-3">
          {data.map((talent) => (
            <TalentRow key={talent.id} talent={talent} />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
          {t("marketplace.empty_directory")}
        </div>
      )}
    </div>
  );
}

/** Annuaire filtrable des talents pour les recruteurs (UC-08). */
export default function TalentsPage() {
  return (
    <RequireRecruiter>
      <TalentsDirectoryContent />
    </RequireRecruiter>
  );
}
