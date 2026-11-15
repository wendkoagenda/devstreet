import { useMemo } from "react";
import { useTranslation } from "react-i18next";
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
  const { t, i18n } = useTranslation();
  const { data: profil, isLoading, isError } = useGetPublicProfileQuery(profilId, { skip: !profilId });

  const nodes = useMemo<OrbitNode[]>(() => {
    if (!profil) return [];
    const place = [profil.city, profil.country && countryName(profil.country, i18n.language)]
      .filter(Boolean)
      .join(", ");
    const links = [profil.github_url, profil.linkedin_url, profil.portfolio_url].filter(Boolean).length;
    const items: OrbitNode[] = [
      {
        key: "skills",
        title: t("marketplace.network.skills"),
        summary:
          profil.skills_detail.length > 0
            ? t("marketplace.network.skills_listed", {
                count: profil.skills_detail.length,
              })
            : t("marketplace.network.none_listed"),
        icon: <Sparkles className="size-4" />,
        onSelect: () => onOpen("dev-skills"),
      },
      {
        key: "experiences",
        title: t("marketplace.network.experiences"),
        summary:
          profil.experiences.length > 0
            ? t("marketplace.network.experiences_listed", {
                count: profil.experiences.length,
              })
            : t("marketplace.network.none_listed"),
        icon: <Briefcase className="size-4" />,
        onSelect: () => onOpen("dev-experiences"),
      },
      {
        key: "reviews",
        title: t("marketplace.network.reviews"),
        summary:
          profil.rating_avg !== null
            ? t("marketplace.network.reviews_summary", {
                avg: profil.rating_avg,
                count: profil.reviews_count,
              })
            : t("marketplace.network.no_reviews_yet"),
        icon: <Star className="size-4" />,
        onSelect: () => onOpen("dev-reviews"),
      },
      {
        key: "infos",
        title: t("marketplace.network.infos"),
        summary: [
          place,
          t("marketplace.network.years_badge", {
            count: profil.years_of_experience,
          }),
        ]
          .filter(Boolean)
          .join(" · "),
        icon: <MapPin className="size-4" />,
        onSelect: () => onOpen(undefined),
      },
    ];
    if (profil.languages.length > 0) {
      items.push({
        key: "languages",
        title: t("marketplace.network.languages"),
        summary: profil.languages.join(", "),
        icon: <Languages className="size-4" />,
        onSelect: () => onOpen("dev-languages"),
      });
    }
    if (links > 0) {
      items.push({
        key: "links",
        title: t("marketplace.network.links"),
        summary: t("marketplace.network.links_count", { count: links }),
        icon: <Link2 className="size-4" />,
        onSelect: () => onOpen(undefined),
      });
    }
    if (profil.can_download_cv) {
      items.push({
        key: "cv",
        title: t("marketplace.network.cv"),
        summary: t("marketplace.network.cv_available"),
        icon: <FileText className="size-4" />,
        onSelect: () => onOpen(undefined),
      });
    }
    return items;
  }, [profil, onOpen, t, i18n.language]);

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (isError || !profil) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
        {t("marketplace.network.profile_hidden")}
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
