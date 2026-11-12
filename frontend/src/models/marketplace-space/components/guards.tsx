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
          <Link to="/marketplace/profile">{cta}</Link>
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

/** Réservé aux recruteurs (profil rattaché à une entreprise) ; sinon explique comment le devenir. */
export function RequireRecruiter({ children }: { children: ReactNode }) {
  const { hasProfil, isRecruiter, isLoading } = useMySpace();
  if (isLoading) return <Loading />;
  if (!hasProfil || !isRecruiter) {
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
