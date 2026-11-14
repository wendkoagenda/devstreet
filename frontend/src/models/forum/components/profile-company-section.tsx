import { Link } from "react-router-dom";
import { BadgeCheck, ExternalLink, Mail, MapPin, Phone } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  OFFER_TYPE_LABELS,
  WORK_MODE_LABELS,
  formatDate,
} from "@/models/marketplace-offers/labels";
import { CreateOfferDialog } from "@/models/marketplace-offers/components/create-offer-dialog";
import { ManageCompanyDialog } from "@/models/marketplace-space/components/manage-company-dialog";
import { CreateCompanyDialog } from "@/models/marketplace-space/components/create-company-dialog";
import { SECTORS, countryName } from "@/models/marketplace-space/options";
import type { MemberProfilEntreprise } from "../api";

/** Onglet « Entreprise » : la société du membre et les offres qu'il a publiées (jamais ses candidatures). */
export function ProfileCompanySection({
  profilEntreprise,
  isOwnProfile,
  onCreated,
}: {
  profilEntreprise: MemberProfilEntreprise | null;
  isOwnProfile: boolean;
  /** Appelé après la création de l'entreprise, pour recharger la page de profil. */
  onCreated?: () => void;
}) {
  if (!profilEntreprise) {
    return (
      <div className="rounded-2xl border border-dashed border-border bg-card px-4 py-10 text-center">
        <p className="mb-3 text-sm text-muted-foreground">
          {isOwnProfile
            ? "Tu n'es rattaché à aucune entreprise. Crée la tienne, ou rejoins-en une sur invitation de son propriétaire."
            : "Ce membre n'a pas de profil entreprise."}
        </p>
        {isOwnProfile ? <CreateCompanyDialog onCreated={onCreated} /> : null}
      </div>
    );
  }

  const { company, offers, is_owner, is_member } = profilEntreprise;
  const sector = SECTORS.find((item) => item.value === company.sector)?.label;
  // Création d'offre en boîte de dialogue : pays et ville de l'entreprise proposés par défaut
  const offerDialog = (
    <CreateOfferDialog
      defaults={{ country: company.country, city: company.city }}
      onCreated={onCreated}
    />
  );

  return (
    <div className="space-y-4">
      <section className="rounded-2xl border border-border bg-card p-4 shadow-sm sm:p-5">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-lg font-semibold text-foreground">{company.name}</h2>
              {company.is_verified ? (
                <Badge variant="secondary" className="gap-1">
                  <BadgeCheck className="size-3.5" aria-hidden />
                  Vérifiée
                </Badge>
              ) : null}
              <Badge variant="outline">{is_owner ? "Propriétaire" : "Membre"}</Badge>
            </div>
            <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
              {sector ? <span>{sector}</span> : null}
              {company.size ? <span>{company.size} personnes</span> : null}
              <span className="inline-flex items-center gap-1">
                <MapPin className="size-3" aria-hidden />
                {[company.city, countryName(company.country)].filter(Boolean).join(", ")}
              </span>
            </p>
          </div>
          {isOwnProfile && is_owner ? <ManageCompanyDialog onChanged={onCreated} /> : null}
        </div>

        {company.description ? (
          <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-foreground">
            {company.description}
          </p>
        ) : null}

        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5 text-xs">
          {company.website ? (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-foreground hover:underline"
            >
              <ExternalLink className="size-3.5" aria-hidden />
              Site web
            </a>
          ) : null}
          {/* Coordonnées sensibles : renvoyées par l'API aux seuls membres de l'entreprise */}
          {is_member && company.contact_email ? (
            <a
              href={`mailto:${company.contact_email}`}
              className="inline-flex items-center gap-1 text-foreground hover:underline"
            >
              <Mail className="size-3.5" aria-hidden />
              {company.contact_email}
            </a>
          ) : null}
          {is_member && company.phone ? (
            <span className="inline-flex items-center gap-1 text-foreground">
              <Phone className="size-3.5" aria-hidden />
              {company.phone}
            </span>
          ) : null}
        </div>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-foreground">Offres de l'entreprise</h3>
          {isOwnProfile && offers.length > 0 ? offerDialog : null}
        </div>
        {offers.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card px-4 py-8 text-center sm:flex-row">
            <p className="text-sm text-muted-foreground">
              Aucune offre publiée pour le moment.
            </p>
            {isOwnProfile ? offerDialog : null}
          </div>
        ) : (
          offers.map((offer) => (
            <Link
              key={offer.id}
              to={`/marketplace/offers/${offer.id}`}
              className="block rounded-2xl border border-border bg-card p-4 shadow-sm transition-colors hover:bg-muted/40"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h4 className="truncate font-semibold text-foreground">{offer.title}</h4>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {[
                      OFFER_TYPE_LABELS[offer.type as keyof typeof OFFER_TYPE_LABELS] ?? offer.type,
                      WORK_MODE_LABELS[offer.work_mode as keyof typeof WORK_MODE_LABELS] ?? offer.work_mode,
                      [offer.city, countryName(offer.country)].filter(Boolean).join(", "),
                      offer.published_at ? formatDate(offer.published_at) : null,
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                </div>
                {offer.status !== "open" ? (
                  <Badge variant="outline">{offer.status === "draft" ? "Brouillon" : "Clôturée"}</Badge>
                ) : null}
              </div>
            </Link>
          ))
        )}
      </section>
    </div>
  );
}
