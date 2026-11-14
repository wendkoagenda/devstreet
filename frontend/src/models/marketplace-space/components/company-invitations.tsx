import { useState } from "react";
import { Copy, Link2, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { formatDate } from "@/models/marketplace-offers/labels";
import {
  useCreateInvitationMutation,
  useGetMyInvitationsQuery,
  useRevokeInvitationMutation,
} from "../api";
import type { InvitationState } from "../schema";

const STATE_LABELS: Record<InvitationState, string> = {
  valid: "En attente",
  expired: "Expirée",
  revoked: "Révoquée",
  accepted: "Acceptée",
};

function errorMessage(error: unknown, fallback: string): string {
  const data = (error as { data?: { error?: string; detail?: string } })?.data;
  return data?.error ?? data?.detail ?? fallback;
}

/** Invitations de l'entreprise : le propriétaire crée un lien (ou envoie un e-mail), suit les états et révoque. */
export function CompanyInvitations() {
  const { data: invitations = [], isLoading } = useGetMyInvitationsQuery();
  const [createInvitation, { isLoading: creating }] = useCreateInvitationMutation();
  const [revokeInvitation] = useRevokeInvitationMutation();
  const [email, setEmail] = useState("");
  // Le lien complet n'est renvoyé qu'à la création : on l'affiche une fois
  const [freshLink, setFreshLink] = useState<string | null>(null);

  const handleCreate = async () => {
    try {
      const result = await createInvitation({ email: email.trim() || undefined }).unwrap();
      setFreshLink(result.link ?? null);
      setEmail("");
      CreationSuccessSonner(result.email ? "Invitation envoyée par e-mail" : "Lien d'invitation créé");
    } catch (error) {
      CreationErrorSonner(errorMessage(error, "Impossible de créer l'invitation"));
    }
  };

  const handleCopy = async () => {
    if (!freshLink) return;
    try {
      await navigator.clipboard.writeText(freshLink);
      CreationSuccessSonner("Lien copié");
    } catch {
      CreationErrorSonner("Copie impossible : sélectionnez le lien à la main");
    }
  };

  const handleRevoke = async (id: number) => {
    try {
      await revokeInvitation(id).unwrap();
      CreationSuccessSonner("Invitation révoquée");
    } catch (error) {
      CreationErrorSonner(errorMessage(error, "Impossible de révoquer l'invitation"));
    }
  };

  return (
    <section className="mt-6 flex flex-col gap-3 border-t border-border pt-5">
      <div>
        <h3 className="text-sm font-semibold text-foreground">Inviter dans l'entreprise</h3>
        <p className="text-xs text-muted-foreground">
          Le lien est valable 7 jours et ne peut servir qu'une fois. Avec une adresse e-mail, le lien lui est envoyé et
          elle seule peut l'utiliser.
        </p>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row">
        <Input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="E-mail de la personne (facultatif)"
          className="h-9"
          aria-label="E-mail de la personne invitée"
        />
        <Button type="button" onClick={handleCreate} disabled={creating} className="shrink-0">
          <Link2 className="mr-2 size-4" aria-hidden />
          Créer l'invitation
        </Button>
      </div>

      {freshLink ? (
        <div className="flex flex-col gap-2 rounded-lg border border-border bg-muted/40 p-3">
          <p className="text-xs text-muted-foreground">
            Copiez ce lien maintenant : il ne sera plus affiché ensuite.
          </p>
          <div className="flex gap-2">
            <Input readOnly value={freshLink} className="h-9 font-mono text-xs" aria-label="Lien d'invitation" />
            <Button type="button" variant="outline" onClick={handleCopy} className="shrink-0">
              <Copy className="mr-2 size-4" aria-hidden />
              Copier
            </Button>
          </div>
        </div>
      ) : null}

      {isLoading ? (
        <p className="text-xs text-muted-foreground">Chargement…</p>
      ) : invitations.length === 0 ? (
        <p className="text-xs text-muted-foreground">Aucune invitation pour le moment.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border rounded-lg border border-border">
          {invitations.map((invitation) => (
            <li key={invitation.id} className="flex items-center justify-between gap-3 px-3 py-2">
              <div className="min-w-0">
                <p className="truncate text-sm text-foreground">{invitation.email || "Lien partageable"}</p>
                <p className="text-xs text-muted-foreground">
                  Créée le {formatDate(invitation.created_at)} · expire le {formatDate(invitation.expires_at)}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <Badge variant={invitation.state === "valid" ? "default" : "secondary"}>
                  {STATE_LABELS[invitation.state]}
                </Badge>
                {invitation.state === "valid" ? (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRevoke(invitation.id)}
                    aria-label="Révoquer l'invitation"
                  >
                    <Trash2 className="size-4" aria-hidden />
                  </Button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
