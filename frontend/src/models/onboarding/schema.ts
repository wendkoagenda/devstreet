import { z } from "zod";
import { companyFormSchema, profilFormSchema } from "@/models/marketplace-space/schema";

/** Étape « Votre profil » : l'essentiel d'un profil dev (le reste se complète plus tard). */
export const devProfilStepSchema = profilFormSchema.pick({
  headline: true,
  country: true,
  city: true,
});
export type DevProfilStepValues = z.infer<typeof devProfilStepSchema>;

/** Étape « Votre entreprise » : l'essentiel d'une entreprise (le reste se complète plus tard). */
export const companyStepSchema = companyFormSchema.pick({
  name: true,
  sector: true,
  size: true,
  country: true,
});
export type CompanyStepValues = z.infer<typeof companyStepSchema>;

/** Types que l'on peut choisir à l'onboarding. */
export const ACCOUNT_TYPE_OPTIONS = [
  {
    value: "dev",
    title: "Développeur",
    description:
      "Présentez vos compétences, trouvez des offres, participez à des projets et échangez sur le forum.",
  },
  {
    value: "entreprise",
    title: "Entreprise",
    description:
      "Publiez des offres et trouvez des talents. Vous accédez à la marketplace et à la messagerie.",
  },
  {
    value: "both",
    title: "Les deux",
    description:
      "Vous développez et vous recrutez : tous les espaces de la plateforme, dev et entreprise.",
  },
] as const;
