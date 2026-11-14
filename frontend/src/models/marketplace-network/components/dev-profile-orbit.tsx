import { useMemo } from "react";
import { Briefcase, FileText, Languages, Link2, MapPin, Sparkles, Star } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ProfileOrbit,
  ProfileOrbitCenter,
  type OrbitNode,
} from "@/models/marketplace-space/components/profile-orbit";
import { countryName } from "@/models/marketplace-space/options";
import { useGetPublicProfileQuery } from "../api";

/** Identifiants des sections de la vue en liste, pour y arriver directement depuis une branche. */
export type DevProfileAnchor = "dev-skills" | "dev-experiences" | "dev-reviews" | "dev-languages" | undefined;

/**
 * Résumé en orbite d'un profil dev, tel que le voient les autres membres : photo, nom, accroche et statut au centre,
 * un compte par branche (compétences, expériences, avis…). Un clic sur une branche ouvre la vue en liste.
 */
export function DevProfileOrbit({
  profilId,
  photo,
  onOpen,
}: {
  profilId: number;
  photo?: string | null;
  /** Ouvre la vue en liste, sur la section demandée. */
  onOpen: (anchor: DevProfileAnchor) => void;
}) {
  const { data: profil, isLoading, isError } = useGetPublicProfileQuery(profilId, { skip: !profilId });

  const nodes = useMemo<OrbitNode[]>(() => {
    if (!profil) return [];
    const place = [profil.city, profil.country && countryName(profil.country)].filter(Boolean).join(", ");
    const links = [profil.github_url, profil.linkedin_url, profil.portfolio_url].filter(Boolean).length;
    const items: OrbitNode[] = [
      {
        key: "skills",
        title: "Compétences",
        summary: profil.skills_detail.length > 0 ? `${profil.skills_detail.length} compétence(s)` : "Aucune renseignée",
        icon: <Sparkles className="size-4" />,
        onSelect: () => onOpen("dev-skills"),
      },
      {
        key: "experiences",
        title: "Expériences",
        summary: profil.experiences.length > 0 ? `${profil.experiences.length} expérience(s)` : "Aucune renseignée",
        icon: <Briefcase className="size-4" />,
        onSelect: () => onOpen("dev-experiences"),
      },
      {
        key: "reviews",
        title: "Avis",
        summary:
          profil.rating_avg !== null
            ? `${profil.rating_avg} / 5 · ${profil.reviews_count} avis`
            : "Pas encore d'avis",
        icon: <Star className="size-4" />,
        onSelect: () => onOpen("dev-reviews"),
      },
      {
        key: "infos",
        title: "Informations",
        summary: [place, `${profil.years_of_experience} an(s) d'expérience`].filter(Boolean).join(" · "),
        icon: <MapPin className="size-4" />,
        onSelect: () => onOpen(undefined),
      },
    ];
    if (profil.languages.length > 0) {
      items.push({
        key: "languages",
        title: "Langues",
        summary: profil.languages.join(", "),
        icon: <Languages className="size-4" />,
        onSelect: () => onOpen("dev-languages"),
      });
    }
    if (links > 0) {
      items.push({
        key: "links",
        title: "Liens",
        summary: `${links} lien(s)`,
        icon: <Link2 className="size-4" />,
        onSelect: () => onOpen(undefined),
      });
    }
    if (profil.can_download_cv) {
      items.push({
        key: "cv",
        title: "CV",
        summary: "Disponible en PDF",
        icon: <FileText className="size-4" />,
        onSelect: () => onOpen(undefined),
      });
    }
    return items;
  }, [profil, onOpen]);

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (isError || !profil) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
        Ce profil dev n'est pas visible : il n'est pas ouvert aux opportunités, ou vous n'avez pas encore de profil.
      </div>
    );
  }

  return (
    <ProfileOrbit
      draggable={false}
      nodes={nodes}
      center={
        <ProfileOrbitCenter
          name={profil.name}
          photo={photo}
          headline={profil.headline}
          openToWork={profil.is_open_to_work}
        />
      }
    />
  );
}
