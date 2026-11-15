import { useEffect } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { Building2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { profilePath } from "@/helpers/routes/profile-path";
import { useAuth } from "@/models/auth/hooks/useAuth";
import { saveRedirectPath } from "@/models/auth/functions/redirect-after-login";
import { useAuthSlice } from "@/models/auth/slice";
import { useAcceptInvitationMutation, useGetInvitationQuery } from "../api";

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <section className="w-full max-w-md rounded-xl border border-border bg-card p-6 text-center shadow-sm">
        {children}
      </section>
    </div>
  );
}

/** Page ouverte depuis un lien d'invitation : affiche l'entreprise et permet de la rejoindre. */
export default function EntrepriseInvitationPage() {
  const { token = "" } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isInitialized } = useAuth();
  const username = useAuthSlice((state) => state.user?.username);
  const loadSession = useAuthSlice((state) => state.loadSession);
  const { data, isLoading, isError } = useGetInvitationQuery(token, {
    skip: !isAuthenticated || !token,
  });
  const [acceptInvitation, { isLoading: accepting }] = useAcceptInvitationMutation();

  // Visiteur non connecté : on mémorise ce lien pour y revenir après la connexion
  useEffect(() => {
    if (isInitialized && !isAuthenticated) saveRedirectPath();
  }, [isInitialized, isAuthenticated]);

  if (!isInitialized) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (isLoading) {
    return (
      <Shell>
        <Skeleton className="mx-auto h-24 w-full" />
      </Shell>
    );
  }

  if (isError || !data) {
    return (
      <Shell>
        <h1 className="mb-2 text-lg font-semibold text-foreground">Invitation introuvable</h1>
        <p className="mb-5 text-sm text-muted-foreground">Ce lien d'invitation n'existe pas ou n'est plus valide.</p>
        <Button asChild variant="outline">
          <Link to="/">Retour à l'accueil</Link>
        </Button>
      </Shell>
    );
  }

  const handleAccept = async () => {
    try {
      const result = await acceptInvitation(token).unwrap();
      CreationSuccessSonner(`Vous avez rejoint ${result.company.name}`);
      // Accepter l'invitation donne le type entreprise : on relit la session (menu, droits, type de compte)
      await loadSession();
      navigate(username ? profilePath(username, "entreprise") : "/", { replace: true });
    } catch (error) {
      const message = (error as { data?: { error?: string } })?.data?.error;
      CreationErrorSonner(message ?? "Impossible d'accepter l'invitation");
    }
  };

  const blocked = data.state !== "valid" ? data.message : null;
  const conflict = data.already_in_company
    ? "Vous êtes déjà rattaché à une entreprise : une seule entreprise par membre."
    : data.email_mismatch
      ? "Cette invitation est destinée à une autre adresse e-mail."
      : null;
  const reason = blocked ?? conflict;

  return (
    <Shell>
      <Building2 className="mx-auto mb-3 size-8 text-muted-foreground" aria-hidden />
      <h1 className="mb-1 text-lg font-semibold text-foreground">Invitation à rejoindre une entreprise</h1>
      <p className="mb-1 flex items-center justify-center gap-2 text-base text-foreground">
        {data.company.name}
        {data.company.is_verified ? <Badge variant="secondary">Vérifiée</Badge> : null}
      </p>
      {reason ? (
        <>
          <p className="my-5 text-sm text-destructive">{reason}</p>
          <Button asChild variant="outline">
            <Link to="/">Retour à l'accueil</Link>
          </Button>
        </>
      ) : (
        <>
          <p className="my-5 text-sm text-muted-foreground">
            En acceptant, vous obtenez un profil entreprise rattaché à cette société et pouvez publier des offres avec
            son équipe.
          </p>
          <Button type="button" onClick={handleAccept} disabled={accepting}>
            Rejoindre l'entreprise
          </Button>
        </>
      )}
    </Shell>
  );
}
