import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Briefcase,
  Building2,
  CalendarDays,
  FileText,
  Handshake,
  Sparkles,
  Star,
  UserRound,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { profilePath } from "@/helpers/routes/profile-path";
import { useAuthSlice } from "@/models/auth/slice";
import { useStats } from "@/models/marketplace-stats/api";
import {
  useGetConnectionsQuery,
  useGetPublicProfileQuery,
} from "@/models/marketplace-network/api";
import { useGetMySkillsQuery } from "@/models/marketplace-offers/api";
import { SkillsCard } from "@/models/marketplace-offers/components/skills-card";
import { formatDate } from "@/models/marketplace-offers/labels";
import { useGetMyExperiencesQuery } from "@/models/marketplace-profile/api";
import { ExperiencesCard } from "@/models/marketplace-profile/components/experiences-card";
import { AVAILABILITY_LABELS } from "@/models/marketplace-profile/schema";
import { CompanyForm } from "../components/company-form";
import { CompanyInvitations } from "../components/company-invitations";
import { ProfileOrbit, ProfileOrbitCenter, type OrbitNode } from "../components/profile-orbit";
import { ProfilForm } from "../components/profil-form";
import { useMySpace } from "../hooks/use-my-space";
import { CV_VISIBILITIES, countryName } from "../options";

type PanelKey =
  | "infos"
  | "skills"
  | "experiences"
  | "company"
  | "reviews"
  | "friends";

const PANEL_TITLES: Record<PanelKey, string> = {
  infos: "Mes informations",
  skills: "Mes compétences",
  experiences: "Mes expériences",
  company: "Mon entreprise",
  reviews: "Mes avis",
  friends: "Mes amis",
};

function ReviewsPanel({ profilId }: { profilId: number }) {
  const { data, isLoading } = useGetPublicProfileQuery(profilId);
  return (
    <Card className="border-0 shadow-none">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Star className="size-4" />
          Mes avis
        </CardTitle>
        <CardDescription>Les avis publics reçus après vos missions.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {isLoading ? <Skeleton className="h-20 w-full" /> : null}
        {data && data.reviews.length === 0 ? (
          <p className="text-sm text-muted-foreground">Pas encore d'avis publics.</p>
        ) : null}
        {data?.reviews.map((review) => (
          <div key={`${review.author}-${review.created_at}`} className="flex flex-col gap-0.5">
            <span className="text-sm font-medium text-foreground">
              {review.author} · {review.rating} / 5
            </span>
            <span className="text-xs text-muted-foreground">{formatDate(review.created_at)}</span>
            {review.comment ? <span className="text-sm text-foreground">{review.comment}</span> : null}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function FriendsPanel() {
  const { data, isLoading, isError, refetch } = useGetConnectionsQuery();
  const friends = data ?? [];

  return (
    <Card className="border-0 shadow-none">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Handshake className="size-4" />
          Mes amis
        </CardTitle>
        <CardDescription>
          Connexions mutuelles : vous vous êtes choisis l’un l’autre.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {isLoading ? <Skeleton className="h-20 w-full" /> : null}
        {isError ? (
          <div className="flex flex-col items-start gap-2">
            <p className="text-sm text-destructive">
              Impossible de charger vos amis.
            </p>
            <Button type="button" size="sm" variant="outline" onClick={() => void refetch()}>
              Réessayer
            </Button>
          </div>
        ) : null}
        {!isLoading && !isError && friends.length === 0 ? (
          <div className="flex flex-col gap-3">
            <p className="text-sm text-muted-foreground">
              Pas encore d’ami. Rencontrez des développeurs : un like réciproque
              crée la connexion.
            </p>
            <Button asChild size="sm">
              <Link to="/marketplace/network">Rencontrer des devs</Link>
            </Button>
          </div>
        ) : null}
        {friends.length > 0 ? (
          <ul className="flex flex-col gap-2">
            {friends.map((friend) => (
              <li key={friend.id}>
                <Link
                  to={
                    friend.username
                      ? profilePath(friend.username, friend.type === "entreprise" ? "entreprise" : "dev")
                      : `/marketplace/profiles/${friend.id}`
                  }
                  className="flex items-center gap-3 rounded-xl border border-border px-3 py-2.5 transition-colors hover:bg-muted/40"
                >
                  <ProfileInitialsAvatar
                    name={friend.name}
                    kind={friend.type === "entreprise" ? "entreprise" : "dev"}
                    openToWork={friend.type !== "entreprise" && friend.is_open_to_work}
                  />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium text-foreground">
                      {friend.name}
                    </span>
                    <span className="block truncate text-xs text-muted-foreground">
                      {friend.headline ||
                        `Connectés le ${formatDate(friend.matched_at)}`}
                    </span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : null}
        {friends.length > 0 ? (
          <Button asChild size="sm" variant="outline">
            <Link to="/marketplace/network">Trouver d’autres amis</Link>
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}

/**
 * « Mon profil pro », affiché dans l'onglet « Profil dev » de ma page de profil : le profil au centre,
 * ses éléments liés (compétences, expériences, entreprise…) en orbite autour.
 */
export function MyProfilePro({ photo }: { photo?: string | null }) {
  const user = useAuthSlice((state) => state.user);
  const { profil, company, isRecruiter, isLoading, isError } = useMySpace();
  const stats = useStats("profile", { skip: !profil });
  const skills = useGetMySkillsQuery(undefined, { skip: !profil });
  const experiences = useGetMyExperiencesQuery(undefined, { skip: !profil });
  const connections = useGetConnectionsQuery(undefined, { skip: !profil });
  const [panel, setPanel] = useState<PanelKey | null>(null);
  const fullName = user?.full_name || user?.email || "";

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

  // Pas encore de profil : on le crée d'abord, l'orbite apparaît ensuite
  if (!profil) {
    return (
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">Créer mon profil</h1>
          <p className="text-sm text-muted-foreground">
            Votre profil est la base de la marketplace : offres recommandées, candidatures et CV automatique.
          </p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <UserRound className="size-4" />
              Mon profil
            </CardTitle>
            <CardDescription>
              Quelques informations suffisent pour commencer, vous pourrez les compléter ensuite.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ProfilForm key="new" profil={null} />
          </CardContent>
        </Card>
      </div>
    );
  }

  const summary = stats.data;
  const skillCount = skills.data?.length ?? 0;
  const experienceCount = experiences.data?.length ?? 0;
  const periodsCount = summary?.availability.periods_count ?? 0;
  const current = summary?.availability.current;
  const rating = summary?.reputation;
  const place = [profil.city, profil.country && countryName(profil.country)].filter(Boolean).join(", ");
  const visibility = CV_VISIBILITIES.find((option) => option.value === profil.cv_visibility)?.label;

  const nodes: OrbitNode[] = [
    {
      key: "skills",
      title: "Compétences",
      summary:
        skillCount > 0
          ? `${skillCount} compétence(s)`
          : "Aucune pour l'instant",
      icon: <Sparkles className="size-4" />,
      todo: skillCount < 3,
      onSelect: () => setPanel("skills"),
    },
    {
      key: "experiences",
      title: "Expériences",
      summary:
        experienceCount > 0
          ? `${experienceCount} expérience(s)`
          : "Aucune pour l'instant",
      icon: <Briefcase className="size-4" />,
      todo: experienceCount === 0,
      onSelect: () => setPanel("experiences"),
    },
    {
      key: "company",
      title: "Entreprise",
      summary: company
        ? `${company.name} · ${profil.is_company_owner ? "propriétaire" : "membre"}`
        : "Créer mon entreprise",
      icon: <Building2 className="size-4" />,
      todo: !company,
      onSelect: () => setPanel("company"),
    },
    {
      key: "availability",
      title: "Disponibilités",
      summary: current
        ? `${AVAILABILITY_LABELS[current.status]} jusqu'au ${formatDate(current.end_date)}`
        : periodsCount > 0
          ? "Calendrier renseigné"
          : "Disponible (aucune période occupée)",
      icon: <CalendarDays className="size-4" />,
      to: "/marketplace/availability",
    },
    {
      key: "cv",
      title: "CV automatique",
      summary: visibility ? `Visible par : ${visibility.toLowerCase()}` : "Aperçu et PDF",
      icon: <FileText className="size-4" />,
      to: "/marketplace/cv",
    },
    {
      key: "friends",
      title: "Mes amis",
      summary:
        (connections.data?.length ?? summary?.connections_count ?? 0) > 0
          ? `${connections.data?.length ?? summary?.connections_count ?? 0} ami(s)`
          : "Aucun ami pour l’instant",
      icon: <Handshake className="size-4" />,
      todo: (connections.data?.length ?? summary?.connections_count ?? 0) === 0,
      onSelect: () => setPanel("friends"),
    },
    {
      key: "reviews",
      title: "Avis",
      summary:
        rating && rating.rating_avg !== null
          ? `${rating.rating_avg} / 5 · ${rating.reviews_count} avis`
          : "Pas encore d'avis",
      icon: <Star className="size-4" />,
      onSelect: () => setPanel("reviews"),
    },
    {
      key: "infos",
      title: "Informations",
      summary: [place, `${profil.years_of_experience} an(s) d'expérience`].filter(Boolean).join(" · "),
      icon: <UserRound className="size-4" />,
      todo: !profil.headline || !profil.bio,
      onSelect: () => setPanel("infos"),
    },
  ];

  const center = (
    <ProfileOrbitCenter
      name={fullName}
      photo={photo ?? user?.photo}
      headline={profil.headline}
      headlinePlaceholder="Ajoutez une accroche pour être mieux repéré."
      openToWork={profil.is_open_to_work}
    />
  );

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <ProfileOrbit
        center={center}
        nodes={nodes}
        storageKey={`marketplace-orbit:${profil.id}`}
      />

      <Sheet open={panel !== null} onOpenChange={(open) => (open ? null : setPanel(null))}>
        <SheetContent side="right" className="w-full overflow-y-auto sm:max-w-xl">
          <SheetTitle className="sr-only">{panel ? PANEL_TITLES[panel] : ""}</SheetTitle>
          <SheetDescription className="sr-only">
            Modifier les éléments liés à votre profil marketplace.
          </SheetDescription>
          <div className="pt-6">
            {panel === "infos" ? (
              <Card className="border-0 shadow-none">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <UserRound className="size-4" />
                    Mes informations
                  </CardTitle>
                  <CardDescription>
                    Ces informations alimentent votre profil public et votre CV.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ProfilForm key={profil.id} profil={profil} />
                </CardContent>
              </Card>
            ) : null}
            {panel === "skills" ? <SkillsCard className="border-0 shadow-none" /> : null}
            {panel === "experiences" ? <ExperiencesCard className="border-0 shadow-none" /> : null}
            {panel === "company" ? (
              <Card className="border-0 shadow-none">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Building2 className="size-4" />
                    Mon entreprise
                    {company?.is_verified ? <Badge variant="secondary">Vérifiée</Badge> : null}
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
                    canEdit={profil.is_company_owner}
                  />
                  {company && profil.is_company_owner ? <CompanyInvitations /> : null}
                </CardContent>
              </Card>
            ) : null}
            {panel === "reviews" ? <ReviewsPanel profilId={profil.id} /> : null}
            {panel === "friends" ? <FriendsPanel /> : null}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
