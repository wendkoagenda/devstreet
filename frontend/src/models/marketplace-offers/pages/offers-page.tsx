import { useState } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { CreateOfferDialog } from "@/models/marketplace-offers/components/create-offer-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { ExploreStatsStrip } from "@/models/marketplace-stats/components/page-stats";
import { RequireMarketplaceMember } from "@/models/marketplace-space/components/guards";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { useGetOffersQuery } from "../api";
import { OFFER_TYPE_LABELS } from "../labels";
import { OfferCard } from "../components/offer-card";

const TYPE_FILTERS = Object.entries(OFFER_TYPE_LABELS);

function OffersContent() {
  const { isRecruiter } = useMySpace();
  const [search, setSearch] = useState("");
  const [type, setType] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const debouncedSearch = useDebouncedValue(search);
  const { data, isFetching, isError } = useGetOffersQuery({
    search: debouncedSearch,
    type,
    work_mode: remoteOnly ? "remote" : "",
  });

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-5">
      <ExploreStatsStrip />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">Offres pour vous</h1>
          <p className="text-sm text-muted-foreground">
            Classées selon la correspondance avec votre profil.
          </p>
        </div>
        {isRecruiter ? (
          <CreateOfferDialog label="Publier une offre" size="default" redirectToList />
        ) : null}
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          className="pl-9"
          placeholder="Rechercher missions, technos, entreprises..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Rechercher une offre"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {TYPE_FILTERS.map(([value, label]) => (
          <Button
            key={value}
            type="button"
            size="sm"
            variant={type === value ? "default" : "outline"}
            aria-pressed={type === value}
            onClick={() => setType(type === value ? "" : value)}
          >
            {label}
          </Button>
        ))}
        <Button
          type="button"
          size="sm"
          variant={remoteOnly ? "default" : "outline"}
          aria-pressed={remoteOnly}
          onClick={() => setRemoteOnly(!remoteOnly)}
        >
          À distance
        </Button>
      </div>

      {isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          Impossible de charger les offres. Réessayez dans un instant.
        </p>
      ) : isFetching && !data ? (
        <div className="flex flex-col gap-3">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : data && data.length > 0 ? (
        <div className="flex flex-col gap-3">
          {data.map((offer) => (
            <OfferCard key={offer.id} offer={offer} to={`/marketplace/offers/${offer.id}`} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-input bg-card p-8 text-center">
          <p className="text-sm text-muted-foreground">
            {isRecruiter
              ? "Aucune offre d’une autre entreprise pour le moment. Vos propres offres sont dans « Mes offres » — vous ne pouvez pas postuler chez vous."
              : "Aucune offre ne correspond pour le moment."}
          </p>
          {isRecruiter ? (
            <Button asChild size="sm" variant="outline">
              <Link to="/marketplace/my-offers">Voir mes offres</Link>
            </Button>
          ) : null}
        </div>
      )}
    </div>
  );
}

/** Missions : offres ouvertes recommandées, avec recherche et filtres. */
export default function OffersPage() {
  return (
    <RequireMarketplaceMember>
      <OffersContent />
    </RequireMarketplaceMember>
  );
}
