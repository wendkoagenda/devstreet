import { z } from "zod";

export const publicationAuteurSchema = z.object({
  id: z.number(),
  username: z.string(),
  full_name: z.string(),
  photo: z.string().optional().default(""),
});

export const publicationImageSchema = z.object({
  id: z.number(),
  publication: z.number(),
  kind: z.enum(["IMAGE", "VIDEO"]).optional().default("IMAGE"),
  url: z.string().url(),
  texte_alternatif: z.string(),
  position: z.number(),
});

export const mediaCommentaireSchema = z.object({
  id: z.number(),
  commentaire: z.number().optional(),
  kind: z.enum(["IMAGE", "VIDEO", "AUDIO"]),
  url: z.string().url(),
  texte_alternatif: z.string().optional().default(""),
  position: z.number().default(0),
});

export const optionPublicationSchema = z.object({
  id: z.number(),
  publication: z.number(),
  libelle: z.string(),
  description: z.string(),
  image_url: z.string().optional().default(""),
  position: z.number().default(0),
  avis_count: z.number().default(0),
});

export const publicationProjetSchema = z
  .object({
    id: z.number(),
    titre: z.string().nullable().optional().default(null),
    slug: z.string().nullable().optional().default(null),
  })
  .nullable()
  .optional()
  .default(null);

export const publicationSchema = z.object({
  id: z.number(),
  auteur: publicationAuteurSchema.nullable(),
  type: z.enum(["DISCUSSION", "APPLICATION", "ENTRAIDE", "CHOIX", "SONDAGE"]),
  titre: z.string(),
  description: z.string(),
  lien_app: z
    .string()
    .optional()
    .default("")
    .refine(
      (value) => value === "" || /^https?:\/\//i.test(value),
      "Le lien doit être une URL HTTP(S)"
    ),
  plateforme_app: z.string().optional().default(""),
  contraintes: z.string().optional().default(""),
  justification_finale: z.string().optional().default(""),
  decided_at: z.string().nullable().optional().default(null),
  reponse_acceptee: z.number().nullable().optional().default(null),
  option_retenue: z.number().nullable().optional().default(null),
  options: z.array(optionPublicationSchema).default([]),
  mon_avis_option_id: z.number().nullable().optional().default(null),
  images: z.array(publicationImageSchema).default([]),
  likes_count: z.number().default(0),
  comments_count: z.number().default(0),
  liked_by_me: z.boolean().default(false),
  saved_by_me: z.boolean().default(false),
  following_auteur: z.boolean().default(false),
  projet: publicationProjetSchema,
  projet_id: z.number().nullable().optional().default(null),
  espace: z
    .object({
      id: z.number(),
      nom: z.string(),
      type: z.enum(["COMMUNAUTE", "CHAINE"]),
      acces: z.enum(["PUBLIC", "LIEN"]).optional().default("PUBLIC"),
      commentaires_ouverts: z.boolean().optional().default(true),
      joined_by_me: z.boolean().optional().default(false),
    })
    .nullable()
    .optional()
    .default(null),
  espace_id: z.number().nullable().optional().default(null),
  created_at: z.string(),
  updated_at: z.string(),
});

const imagesDataSchema = z
  .array(
    z.object({
      url: z.string().url("URL de média invalide"),
      kind: z.enum(["IMAGE", "VIDEO"]).optional().default("IMAGE"),
      texte_alternatif: z.string().max(200).optional().default(""),
      position: z.number().int().min(0).optional().default(0),
    })
  )
  .max(10)
  .optional()
  .default([]);

const mediasCommentDataSchema = z
  .array(
    z.object({
      // Chemins relatifs (/media/…) ou URLs absolues acceptés.
      url: z.string().trim().min(1, "URL de média invalide"),
      kind: z.enum(["IMAGE", "VIDEO", "AUDIO"]).default("IMAGE"),
      texte_alternatif: z.string().max(200).optional().default(""),
      position: z.number().int().min(0).optional().default(0),
    })
  )
  .max(4)
  .optional()
  .default([]);

export const espaceSchema = z.object({
  id: z.number(),
  type: z.enum(["COMMUNAUTE", "CHAINE"]),
  nom: z.string(),
  description: z.string().optional().default(""),
  photo: z.string().optional().default(""),
  acces: z.enum(["PUBLIC", "LIEN"]),
  membres_peuvent_publier: z.boolean().default(true),
  commentaires_ouverts: z.boolean().default(true),
  mon_role: z
    .enum(["SUPER_ADMIN", "ADMIN", "MEMBRE"])
    .nullable()
    .optional()
    .default(null),
  membres_count: z.number().optional().default(0),
  can_read: z.boolean().optional().default(true),
  can_interact: z.boolean().optional().default(false),
  can_publish: z.boolean().optional().default(false),
  via_preview: z.boolean().optional().default(false),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const createEspaceSchema = z.object({
  nom: z.string().trim().min(1, "Le nom est obligatoire").max(120),
  description: z.string().trim().optional().default(""),
  type: z.enum(["COMMUNAUTE", "CHAINE"]).optional().default("COMMUNAUTE"),
  membres_peuvent_publier: z.boolean().optional().default(true),
  acces: z.enum(["PUBLIC", "LIEN"]).optional().default("PUBLIC"),
  commentaires_ouverts: z.boolean().optional().default(true),
});

export const lienInvitationSchema = z.object({
  id: z.number(),
  espace: z.number(),
  cree_par: z.number(),
  previsualisation_autorisee: z.boolean(),
  revoked_at: z.string().nullable().optional(),
  est_actif: z.boolean().optional().default(true),
  code: z.string().optional(),
  created_at: z.string().optional(),
});

export const espaceMembreSchema = z.object({
  id: z.number(),
  espace: z.number(),
  membre: z.number(),
  membre_detail: z
    .object({
      id: z.number(),
      username: z.string(),
      full_name: z.string(),
      photo: z.string().optional().default(""),
    })
    .nullable()
    .optional(),
  role: z.enum(["SUPER_ADMIN", "ADMIN", "MEMBRE"]),
  joined_at: z.string().nullable().optional(),
});

export const createDiscussionSchema = z.object({
  titre: z.string().trim().min(1, "Le titre est obligatoire").max(200),
  description: z.string().trim().min(1, "Le contenu est obligatoire"),
  images_data: imagesDataSchema,
  espace_id: z.number().int().positive().nullable().optional(),
});

export const createApplicationSchema = z.object({
  titre: z.string().trim().min(1, "Le titre est obligatoire").max(200),
  description: z.string().trim().min(1, "La description est obligatoire"),
  lien_app: z
    .string()
    .trim()
    .url("Lien invalide")
    .refine(
      (value) => value.startsWith("http://") || value.startsWith("https://"),
      "Le lien doit commencer par http:// ou https://"
    ),
  plateforme_app: z.enum(["WEB", "MOBILE", "LES_DEUX"]).default("WEB"),
  images_data: imagesDataSchema,
});

export const createEntraideSchema = z.object({
  titre: z.string().trim().min(1, "Le titre est obligatoire").max(200),
  description: z
    .string()
    .trim()
    .min(1, "Décris le problème (texte et/ou code)"),
  images_data: imagesDataSchema,
});

export const createChoixSchema = z.object({
  titre: z.string().trim().min(1, "Le titre est obligatoire").max(200),
  description: z.string().trim().min(1, "Le contexte est obligatoire"),
  contraintes: z.string().optional().default(""),
  options_data: z
    .array(
      z.object({
        libelle: z.string().trim().min(1, "Libellé obligatoire").max(200),
        description: z.string().trim().optional().default(""),
        image_url: z.string().url().optional().or(z.literal("")),
        position: z.number().int().min(0).optional().default(0),
      })
    )
    .min(2, "Au moins deux options sont requises"),
  images_data: imagesDataSchema,
});

export const upsertAvisSchema = z.object({
  option_id: z.number().int().positive(),
  explication: z.string().trim().optional().default(""),
});

export const decideChoixSchema = z.object({
  option_id: z.number().int().positive(),
  justification_finale: z
    .string()
    .trim()
    .min(1, "La justification est obligatoire"),
});

export const commentNatureSchema = z.enum([
  "COMMENTAIRE",
  "RETOUR_APP",
  "REPONSE_TECHNIQUE",
]);

export const createCommentSchema = z
  .object({
    texte: z.string().trim().optional().default(""),
    parent_id: z.number().int().positive().nullable().optional(),
    option_id: z.number().int().positive().nullable().optional(),
    est_anonyme: z.boolean().optional().default(false),
    nature: commentNatureSchema.optional().default("COMMENTAIRE"),
    medias_data: mediasCommentDataSchema,
  })
  .superRefine((value, ctx) => {
    const hasText = Boolean(value.texte?.trim());
    const hasMedia = (value.medias_data?.length ?? 0) > 0;
    if (!hasText && !hasMedia) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Ajoute un texte ou un média",
        path: ["texte"],
      });
    }
  });

export type PublicationAuteur = z.infer<typeof publicationAuteurSchema>;
export type PublicationImage = z.infer<typeof publicationImageSchema>;
export type MediaCommentaire = z.infer<typeof mediaCommentaireSchema>;
export type OptionPublication = z.infer<typeof optionPublicationSchema>;
export type Publication = z.infer<typeof publicationSchema>;
export type Espace = z.infer<typeof espaceSchema>;
export type CreateEspaceInput = z.infer<typeof createEspaceSchema>;
/** Corps envoyé à l'API : les champs à valeur par défaut sont facultatifs (le serveur les complète). */
export type CreateEspaceBody = z.input<typeof createEspaceSchema>;
export type LienInvitation = z.infer<typeof lienInvitationSchema>;
export type EspaceMembre = z.infer<typeof espaceMembreSchema>;
export type CreateDiscussionInput = z.infer<typeof createDiscussionSchema>;
export type CreateApplicationInput = z.infer<typeof createApplicationSchema>;
export type CreateEntraideInput = z.infer<typeof createEntraideSchema>;
export type CreateChoixInput = z.infer<typeof createChoixSchema>;
export type UpsertAvisInput = z.infer<typeof upsertAvisSchema>;
export type DecideChoixInput = z.infer<typeof decideChoixSchema>;
export type CreateCommentInput = z.infer<typeof createCommentSchema>;
export type CreateCommentFormValues = z.input<typeof createCommentSchema>;
export type CommentNature = z.infer<typeof commentNatureSchema>;

export type AvisChoix = {
  id: number;
  membre: PublicationAuteur | null;
  option: number;
  explication: string;
  created_at: string;
  updated_at: string;
};

export type Commentaire = {
  id: number;
  publication: number;
  auteur: PublicationAuteur | null;
  parent: number | null;
  option: number | null;
  option_libelle: string | null;
  nature: CommentNature;
  texte: string;
  est_anonyme: boolean;
  medias?: MediaCommentaire[];
  likes_count: number;
  liked_by_me: boolean;
  confirmations_count: number;
  confirmed_by_me: boolean;
  reponses: Commentaire[];
  created_at: string;
  updated_at: string;
  created_by?: number;
  updated_by?: number;
};

export type FavoriToggleResult = {
  saved: boolean;
  publication_id: number;
};

export type LikeToggleResult = {
  liked: boolean;
  likes_count: number;
  publication_id?: number;
  commentaire_id?: number;
};

export type ConfirmationAideToggleResult = {
  confirmed: boolean;
  confirmations_count: number;
  commentaire_id: number;
};
