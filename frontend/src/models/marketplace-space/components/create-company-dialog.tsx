import { useState } from "react";
import { Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { CompanyStepsForm } from "./company-steps-form";

/**
 * Bouton « Créer mon entreprise » : ouvre une boîte de dialogue avec le formulaire de l'entreprise,
 * sans quitter la page. À la création, le membre devient propriétaire et obtient son profil entreprise.
 */
export function CreateCompanyDialog({ onCreated }: { onCreated?: () => void }) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button type="button">
          <Building2 className="mr-2 size-4" aria-hidden />
          Créer mon entreprise
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Créer mon entreprise</DialogTitle>
          <DialogDescription>
            Renseignez votre entreprise en trois étapes. Vous en deviendrez le propriétaire et pourrez inviter votre
            équipe et publier des offres.
          </DialogDescription>
        </DialogHeader>
        <CompanyStepsForm
          onCreated={() => {
            setOpen(false);
            onCreated?.();
          }}
        />
      </DialogContent>
    </Dialog>
  );
}
