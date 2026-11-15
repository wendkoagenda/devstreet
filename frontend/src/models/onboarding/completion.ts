import type { MyCompany, MyProfil } from "@/models/marketplace-space/schema";

export type CompletionItem = {
  id: string;
  label: string;
  done: boolean;
  /** Formulaire complet où compléter cet élément. */
  href: string;
};

type CompletionInput = {
  wantsDev: boolean;
  wantsEntreprise: boolean;
  profil: MyProfil | null;
  company: MyCompany | null;
  skillsCount: number;
};

/** Éléments du récapitulatif de fin d'assistant, selon les types de compte du membre. */
export function buildCompletionItems({
  wantsDev,
  wantsEntreprise,
  profil,
  company,
  skillsCount,
}: CompletionInput): CompletionItem[] {
  const items: CompletionItem[] = [];

  if (wantsDev) {
    const devHref = "/profil/me?section=dev";
    items.push(
      { id: "dev-profil", label: "Profil dev créé", done: profil !== null, href: devHref },
      { id: "dev-skills", label: "Compétences ajoutées", done: skillsCount > 0, href: devHref },
      { id: "dev-bio", label: "Présentation rédigée", done: Boolean(profil?.bio), href: devHref },
      {
        id: "dev-links",
        label: "Liens (GitHub, LinkedIn, portfolio)",
        done: Boolean(profil?.github_url || profil?.linkedin_url || profil?.portfolio_url),
        href: devHref,
      }
    );
  }

  if (wantsEntreprise) {
    const companyHref = "/profil/me?section=entreprise";
    items.push(
      { id: "company-created", label: "Entreprise créée", done: company !== null, href: companyHref },
      { id: "company-description", label: "Description de l'entreprise", done: Boolean(company?.description), href: companyHref },
      {
        id: "company-contact",
        label: "Contact (e-mail ou site web)",
        done: Boolean(company?.contact_email || company?.website),
        href: companyHref,
      }
    );
  }

  return items;
}

/** Niveau de complétion en pourcentage (0 sans élément). */
export function completionPercent(items: CompletionItem[]): number {
  if (items.length === 0) return 0;
  return Math.round((items.filter((item) => item.done).length / items.length) * 100);
}
