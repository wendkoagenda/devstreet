import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useMySpace } from "../hooks/use-my-space";

function Gate({ title, text, cta }: { title: string; text: string; cta: string }) {
  return (
    <div className="mx-auto w-full max-w-lg">
      <section className="flex flex-col items-center rounded-xl border border-dashed border-input bg-card px-6 py-14 text-center shadow-sm">
        <h1 className="mb-2 text-xl font-semibold text-foreground">{title}</h1>
        <p className="mb-6 max-w-md text-sm text-muted-foreground">{text}</p>
        <Button asChild>
          <Link to="/profil/me?section=dev">{cta}</Link>
        </Button>
      </section>
    </div>
  );
}

function Loading() {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
      <Skeleton className="h-16 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

/** Affiche son contenu seulement si l'utilisateur a un profil marketplace ; sinon l'invite à le créer. */
export function RequireProfil({ children }: { children: ReactNode }) {
  const { hasProfil, isLoading } = useMySpace();
  if (isLoading) return <Loading />;
  if (!hasProfil) {
    return (
      <Gate
        title="Créez votre profil pour continuer"
        text="Votre profil marketplace est nécessaire pour voir les offres, postuler et être recommandé."
        cta="Créer mon profil"
      />
    );
  }
  return <>{children}</>;
}

/** Affiche son contenu si le membre a un profil dev ou un profil entreprise ; sinon l'invite à créer un profil. */
export function RequireMarketplaceMember({ children }: { children: ReactNode }) {
  const { hasAnyProfile, isLoading } = useMySpace();
  if (isLoading) return <Loading />;
  if (!hasAnyProfile) {
    return (
      <Gate
        title="Créez votre profil pour continuer"
        text="Un profil dev ou une entreprise est nécessaire pour utiliser la marketplace."
        cta="Créer mon profil"
      />
    );
  }
  return <>{children}</>;
}

/** Réservé aux recruteurs (profil entreprise) ; sinon explique comment le devenir. */
export function RequireRecruiter({ children }: { children: ReactNode }) {
  const { hasProfil, isRecruiter, isLoading } = useMySpace();
  if (isLoading) return <Loading />;
  // Un membre invité n'a qu'un profil entreprise : le profil dev n'est pas nécessaire pour recruter
  if (!isRecruiter) {
    return (
      <Gate
        title="Espace recruteur"
        text="Pour publier des offres et découvrir des talents, créez d'abord votre profil, puis votre entreprise."
        cta={hasProfil ? "Créer mon entreprise" : "Créer mon profil"}
      />
    );
  }
  return <>{children}</>;
}
