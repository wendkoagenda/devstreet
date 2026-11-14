import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus } from "lucide-react";
import { Button, type ButtonProps } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import type { Offer } from "../schema";
import { OfferStepsForm } from "./offer-steps-form";

type CreateOfferDialogProps = {
  /** Pays et ville proposés pour la nouvelle offre ; par défaut, ceux de l'entreprise. */
  defaults?: { country?: string; city?: string };
  /** Appelé après la création, avec l'offre créée. */
  onCreated?: (offer: Offer) => void;
  /** Mène à « Mes offres » après la création (pour les écrans qui n'affichent pas la liste des offres). */
  redirectToList?: boolean;
  label?: string;
  size?: ButtonProps["size"];
  variant?: ButtonProps["variant"];
};

/**
 * Création d'une offre : une boîte de dialogue en plusieurs étapes, ouverte depuis un bouton, sans quitter la page.
 * C'est le seul endroit où l'on crée une offre (il n'y a plus de page dédiée).
 */
export function CreateOfferDialog({
  defaults,
  onCreated,
  redirectToList = false,
  label = "Créer une offre",
  size = "sm",
  variant,
}: CreateOfferDialogProps) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { company } = useMySpace();
  const resolvedDefaults = defaults ?? { country: company?.country, city: company?.city };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button type="button" size={size} variant={variant}>
          <Plus className="mr-1.5 size-4" aria-hidden />
          {label}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Créer une offre</DialogTitle>
          <DialogDescription>
            Décrivez votre besoin en quatre étapes. Vous pourrez publier l'offre tout de suite ou la garder en
            brouillon.
          </DialogDescription>
        </DialogHeader>
        <OfferStepsForm
          defaults={resolvedDefaults}
          onSaved={(offer) => {
            setOpen(false);
            onCreated?.(offer);
            if (redirectToList) navigate("/marketplace/my-offers");
          }}
        />
      </DialogContent>
    </Dialog>
  );
}
