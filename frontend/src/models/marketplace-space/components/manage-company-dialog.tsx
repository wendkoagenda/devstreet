import { useState } from "react";
import { Settings2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useMySpace } from "../hooks/use-my-space";
import { CompanyForm } from "./company-form";
import { CompanyInvitations } from "./company-invitations";

/**
 * « Gérer l'entreprise » : le propriétaire modifie les informations de sa société et invite son équipe,
 * dans une boîte de dialogue, sans quitter la page de profil.
 */
export function ManageCompanyDialog({ onChanged }: { onChanged?: () => void }) {
  const { company } = useMySpace();
  const [open, setOpen] = useState(false);
  if (!company) return null;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button type="button" variant="outline" size="sm">
          <Settings2 className="mr-1.5 size-4" aria-hidden />
          Gérer l'entreprise
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {company.name}
            {company.is_verified ? <Badge variant="secondary">Vérifiée</Badge> : null}
          </DialogTitle>
          <DialogDescription>
            Modifiez les informations de votre entreprise et invitez les membres de votre équipe.
          </DialogDescription>
        </DialogHeader>
        <CompanyForm key={company.id} company={company} canEdit onUpdated={onChanged} />
        <CompanyInvitations />
      </DialogContent>
    </Dialog>
  );
}
