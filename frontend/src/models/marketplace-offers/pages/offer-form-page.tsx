import { Link, useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { useGetMyOfferQuery } from "../api";
import { OfferStepsForm } from "../components/offer-steps-form";

function OfferFormContent() {
  const { id } = useParams();
  const navigate = useNavigate();
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
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Détail de l'offre</CardTitle>
        </CardHeader>
        <CardContent>
          <OfferStepsForm
            key={offer?.id ?? "new"}
            offer={isEdit ? (offer ?? null) : null}
            defaults={{ country: company?.country, city: company?.city }}
            onSaved={(saved) => navigate(`/marketplace/my-offers/${saved.id}`)}
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
