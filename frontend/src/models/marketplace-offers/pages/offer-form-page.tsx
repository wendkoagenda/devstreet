import { Link, useParams } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { useGetMyOfferQuery } from "../api";
import { OfferForm } from "../components/offer-form";

/** Emplacement de l'assistant IA (rédaction de l'offre) : annoncé, désactivé tant que l'IA n'est pas branchée. */
function AiAssistantPlaceholder() {
  return (
    <Card className="border-dashed">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Sparkles className="size-4" aria-hidden />
          Décrivez votre besoin, l'IA rédige l'offre
        </CardTitle>
        <Badge variant="secondary">Bientôt disponible</Badge>
      </CardHeader>
      <CardContent>
        <Textarea
          disabled
          rows={2}
          aria-label="Votre besoin, en une ou deux phrases"
          placeholder="Ex. J'ai besoin d'une application de livraison pour mon restaurant, avec suivi des commandes."
        />
      </CardContent>
    </Card>
  );
}

function OfferFormContent() {
  const { id } = useParams();
  const { company } = useMySpace();
  const isEdit = Boolean(id);
  const { data: offer, isLoading, isError } = useGetMyOfferQuery(Number(id), { skip: !isEdit });

  if (isEdit && isLoading) {
    return <Skeleton className="mx-auto h-96 w-full max-w-3xl" />;
  }
  if (isEdit && (isError || !offer)) {
    return (
      <div className="mx-auto w-full max-w-3xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        Cette offre n'existe pas.{" "}
        <Link to="/marketplace/my-offers" className="underline">
          Retour à mes offres
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
      <h1 className="text-xl font-semibold text-foreground">
        {isEdit ? "Modifier l'offre" : "Publier une offre"}
      </h1>
      {isEdit ? null : <AiAssistantPlaceholder />}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Détail de l'offre</CardTitle>
        </CardHeader>
        <CardContent>
          <OfferForm
            key={offer?.id ?? "new"}
            offer={isEdit ? (offer ?? null) : null}
            defaults={{ country: company?.country, city: company?.city }}
          />
        </CardContent>
      </Card>
    </div>
  );
}

/** Création et modification d'une offre (recruteur). */
export default function OfferFormPage() {
  return (
    <RequireRecruiter>
      <OfferFormContent />
    </RequireRecruiter>
  );
}
