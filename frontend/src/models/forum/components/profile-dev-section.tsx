import { useCallback, useEffect, useState } from "react";
import { List, Orbit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  DevProfileOrbit,
  type DevProfileAnchor,
} from "@/models/marketplace-network/components/dev-profile-orbit";
import { DevProfileView } from "@/models/marketplace-network/pages/profile-view-page";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { MyProfilePro } from "@/models/marketplace-space/pages/my-profile-page";
import type { MemberProfilDev } from "../api";

type View = "orbit" | "list";

const VIEW_STORAGE_KEY = "profile-dev-view";

function loadView(): View {
  try {
    return window.localStorage.getItem(VIEW_STORAGE_KEY) === "list" ? "list" : "orbit";
  } catch {
    return "orbit";
  }
}

/** Choix de l'affichage : résumé en orbite ou fiche détaillée en liste (mémorisé sur cet appareil). */
function ViewSwitch({ view, onChange }: { view: View; onChange: (view: View) => void }) {
  const options: { id: View; label: string; icon: typeof Orbit }[] = [
    { id: "orbit", label: "Orbite", icon: Orbit },
    { id: "list", label: "Liste", icon: List },
  ];
  return (
    <div
      role="group"
      aria-label="Affichage du profil dev"
      className="inline-flex rounded-xl border border-brand-soft-border bg-card p-1 shadow-sm"
    >
      {options.map(({ id, label, icon: Icon }) => (
        <Button
          key={id}
          type="button"
          size="sm"
          variant="ghost"
          aria-pressed={view === id}
          onClick={() => onChange(id)}
          className={cn(
            "h-8 gap-1.5 rounded-lg px-3",
            view === id ? "bg-brand-soft text-brand-strong hover:bg-brand-soft" : "text-muted-foreground"
          )}
        >
          <Icon className="size-4" aria-hidden />
          {label}
        </Button>
      ))}
    </div>
  );
}

/**
 * Onglet « Profil dev », visible par tous les membres connectés.
 * - Orbite : résumé du profil (photo, nom, accroche, statut au centre ; un compte par branche).
 *   Sur mon profil, les branches ouvrent l'édition ; sur celui d'un autre membre, la fiche en liste.
 * - Liste : la fiche détaillée (compétences, expériences, avis, coordonnées, CV).
 */
export function ProfileDevSection({
  profilDev,
  isOwnProfile,
  photo,
}: {
  profilDev: MemberProfilDev | null;
  isOwnProfile: boolean;
  photo?: string | null;
}) {
  const [view, setViewState] = useState<View>(loadView);
  const [anchor, setAnchor] = useState<DevProfileAnchor>(undefined);
  const { profil } = useMySpace();

  const setView = useCallback((next: View) => {
    setViewState(next);
    try {
      window.localStorage.setItem(VIEW_STORAGE_KEY, next);
    } catch (error) {
      console.warn("Affichage du profil dev non mémorisé (stockage bloqué)", error);
    }
  }, []);

  // Depuis une branche : ouvre la liste puis amène la section demandée à l'écran
  const openList = useCallback(
    (target: DevProfileAnchor) => {
      setAnchor(target);
      setView("list");
    },
    [setView]
  );

  useEffect(() => {
    if (view !== "list" || !anchor) return;
    // La fiche se charge après l'ouverture : on réessaie brièvement jusqu'à ce que la section existe
    let tries = 0;
    const timer = window.setInterval(() => {
      const target = document.getElementById(anchor);
      tries += 1;
      if (target || tries > 20) {
        window.clearInterval(timer);
        target?.scrollIntoView({ behavior: "smooth", block: "start" });
        setAnchor(undefined);
      }
    }, 100);
    return () => window.clearInterval(timer);
  }, [view, anchor]);

  const profilId = isOwnProfile ? profil?.id : profilDev?.id;

  // Mon profil dev n'existe pas encore : le formulaire de création s'affiche (pas de choix d'affichage)
  if (isOwnProfile && !profil) return <MyProfilePro photo={photo} />;

  if (!profilId) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
        Ce membre n'a pas de profil dev.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <ViewSwitch view={view} onChange={setView} />
      </div>

      {view === "list" ? (
        <DevProfileView profilId={profilId} onEdit={isOwnProfile ? () => setView("orbit") : undefined} />
      ) : isOwnProfile ? (
        <MyProfilePro photo={photo} />
      ) : (
        <DevProfileOrbit profilId={profilId} photo={photo} onOpen={openList} />
      )}
    </div>
  );
}
