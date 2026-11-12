import { Building2, UserRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthSlice } from "@/models/auth/slice";
import { CompanyForm } from "../components/company-form";
import { ProfilForm } from "../components/profil-form";
import { useMySpace } from "../hooks/use-my-space";
import { countryName } from "../options";

function initialsOf(name: string | undefined | null): string {
  if (!name) return "?";
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

/** « Mon profil » : création du profil marketplace, puis modification de ses informations et de son entreprise. */
export default function MyProfilePage() {
  const user = useAuthSlice((state) => state.user);
  const { profil, company, hasProfil, isRecruiter, isLoading, isError } =
    useMySpace();
  const fullName = user?.full_name || user?.email;

  if (isLoading) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto w-full max-w-3xl rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
        Impossible de charger votre profil. Réessayez dans un instant.
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <div className="flex flex-wrap items-center gap-4">
        <div
          className="flex size-14 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-base font-semibold text-foreground"
          aria-hidden
        >
          {initialsOf(fullName)}
        </div>
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <h1 className="truncate text-xl font-semibold text-foreground">
            {hasProfil ? fullName : "Créer mon profil"}
          </h1>
          <p className="text-sm text-muted-foreground">
            {hasProfil
              ? [profil?.headline, profil?.city, profil?.country && countryName(profil.country)]
                  .filter(Boolean)
                  .join(" · ") || "Complétez votre accroche pour être mieux repéré."
              : "Votre profil est la base de la marketplace : offres recommandées, candidatures et CV automatique."}
          </p>
        </div>
        {hasProfil ? (
          <div className="flex flex-wrap gap-2">
            <Badge variant={profil?.is_open_to_work ? "default" : "secondary"}>
              {profil?.is_open_to_work
                ? "Ouvert aux opportunités"
                : "Non disponible"}
            </Badge>
            {isRecruiter ? (
              <Badge variant="outline">Recruteur · {company?.name}</Badge>
            ) : null}
          </div>
        ) : null}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <UserRound className="size-4" />
            {hasProfil ? "Mes informations" : "Mon profil"}
          </CardTitle>
          <CardDescription>
            {hasProfil
              ? "Ces informations alimentent votre profil public et votre CV."
              : "Quelques informations suffisent pour commencer, vous pourrez les compléter ensuite."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProfilForm key={profil?.id ?? "new"} profil={profil} />
        </CardContent>
      </Card>

      {hasProfil ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Building2 className="size-4" />
              Mon entreprise
              {company?.is_verified ? (
                <Badge variant="secondary">Vérifiée</Badge>
              ) : null}
            </CardTitle>
            <CardDescription>
              {isRecruiter
                ? "Les offres que vous publiez sont rattachées à cette entreprise."
                : "Vous recrutez ? Créez votre entreprise pour publier des offres et découvrir des talents."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CompanyForm
              key={company?.id ?? "new"}
              company={company}
              canEdit={profil?.is_company_owner ?? false}
            />
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
