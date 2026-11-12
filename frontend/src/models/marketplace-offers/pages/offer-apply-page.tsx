import { useState, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { FileText } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { useApplyToOfferMutation, useGetOfferQuery } from "../api";

function OfferApplyContent() {
  const { id } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { data: offer, isLoading } = useGetOfferQuery(Number(id), { skip: !id });
  const [apply, { isLoading: isSending }] = useApplyToOfferMutation();
  const [message, setMessage] = useState("");
  const [error, setError] = useState<ReactNode>(null);

  if (isLoading) {
    return <Skeleton className="mx-auto h-64 w-full max-w-3xl" />;
  }
  if (!offer || offer.status !== "open" || offer.is_own || offer.my_candidature) {
    return (
      <div className="mx-auto w-full max-w-3xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        Vous ne pouvez pas postuler à cette offre.{" "}
        <Link to="/marketplace/offers" className="underline">
          Retour aux offres
        </Link>
      </div>
    );
  }

  const send = async () => {
    setError(null);
    try {
      await apply({ id: offer.id, message: message.trim() }).unwrap();
      CreationSuccessSonner("Candidature envoyée");
      navigate("/marketplace/applications");
    } catch (err) {
      setError(renderFetchBaseQueryError(err as FetchBaseQueryError, t));
    }
  };

  return (
    <Card className="mx-auto w-full max-w-3xl">
      <CardHeader>
        <CardTitle className="text-lg">Postuler à « {offer.title} »</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        {error}
        <div className="flex flex-col gap-2">
          <Label htmlFor="apply-message">Message à l'entreprise</Label>
          <Textarea
            id="apply-message"
            rows={6}
            maxLength={5000}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={`Présentez-vous à ${offer.company.name} en quelques lignes.`}
          />
        </div>

        <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/40 p-3">
          <FileText className="size-5 shrink-0 text-muted-foreground" aria-hidden />
          <span className="flex flex-1 flex-col text-sm">
            <span className="font-medium text-foreground">CV automatique</span>
            <span className="text-xs text-muted-foreground">
              Généré depuis votre profil, vos compétences et vos expériences.
            </span>
          </span>
          <Button asChild size="sm" variant="outline">
            <Link to="/marketplace/cv" target="_blank" rel="noopener noreferrer">
              Aperçu
            </Link>
          </Button>
        </div>

        <div className="flex flex-wrap justify-end gap-2">
          <Button asChild variant="outline">
            <Link to={`/marketplace/offers/${offer.id}`}>Annuler</Link>
          </Button>
          <Button type="button" disabled={isSending} onClick={send}>
            Envoyer ma candidature
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

/** Candidature à une offre : message à l'entreprise ; le CV est celui du profil. */
export default function OfferApplyPage() {
  return (
    <RequireProfil>
      <OfferApplyContent />
    </RequireProfil>
  );
}
