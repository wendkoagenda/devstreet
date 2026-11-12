import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate, initialsOf } from "@/models/marketplace-offers/labels";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useGetPoolQuery } from "../api";

function PoolContent() {
  const { data, isLoading, isError } = useGetPoolQuery();

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">Mon vivier de talents</h1>
          <p className="text-sm text-muted-foreground">
            Les profils gardés par les recruteurs de votre entreprise.
          </p>
        </div>
        <Button asChild variant="outline">
          <Link to="/marketplace/talents">Découvrir des profils</Link>
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-40 w-full" />
      ) : isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          Impossible de charger le vivier.
        </p>
      ) : data && data.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((talent) => (
            <Card key={talent.id}>
              <CardContent className="flex flex-col gap-3 p-4">
                <div className="flex items-center gap-3">
                  <span
                    className="flex size-10 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-xs font-semibold"
                    aria-hidden
                  >
                    {initialsOf(talent.name)}
                  </span>
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
                  Gardé par {talent.liked_by} le {formatDate(talent.liked_at)}
                </span>
                <div className="flex gap-2">
                  <Button asChild size="sm" className="flex-1">
                    <Link to={`/marketplace/profiles/${talent.id}`}>Voir le profil</Link>
                  </Button>
                  {talent.email ? (
                    <Button asChild size="sm" variant="outline">
                      <a href={`mailto:${talent.email}`}>Contacter</a>
                    </Button>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
          Votre vivier est vide : gardez des profils en glissant leur carte vers la droite.
          <Button asChild>
            <Link to="/marketplace/talents">Découvrir des profils</Link>
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
