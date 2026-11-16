export type LegalSection = {
  id: string;
  title: string;
  paragraphs: string[];
  bullets?: string[];
};

export type LegalDocument = {
  slug: "confidentialite" | "conditions";
  title: string;
  updatedAt: string;
  intro: string;
  disclaimer: string;
  sections: LegalSection[];
};

const PRIVACY_FR: LegalDocument = {
  slug: "confidentialite",
  title: "Politique de confidentialité",
  updatedAt: "16 novembre 2026",
  intro:
    "DevStreet (« nous ») édite une plateforme destinée en priorité aux développeurs et aux entreprises tech en Afrique et dans la diaspora. Cette politique explique quelles données personnelles nous traitons, pourquoi, combien de temps, avec qui, et quels droits vous pouvez exercer.",
  disclaimer:
    "Ce document s'inspire du Règlement (UE) 2016/679 (RGPD), de la Convention de l'Union africaine sur la cybersécurité et la protection des données personnelles (Malabo, 2014), et des principes communs aux lois nationales africaines (notamment NDPA/NDPR au Nigeria, Data Protection Act 2019 au Kenya, POPIA en Afrique du Sud, Loi n° 09-08 au Maroc, Loi n° 2008-12 au Sénégal, et les cadres de protection des données en vigueur au Burkina Faso et dans d'autres États membres de la CEDEAO). Il ne constitue pas un conseil juridique personnalisé.",
  sections: [
    {
      id: "responsable",
      title: "1. Responsable du traitement",
      paragraphs: [
        "Le responsable du traitement des données collectées via la plateforme DevStreet est l'éditeur de DevStreet. Pour toute question relative à vos données personnelles, vous pouvez écrire à privacy@devstreet.app.",
        "Selon le pays depuis lequel vous utilisez le service, une autorité nationale de protection des données peut être compétente pour recevoir une réclamation (par exemple la CNIL en France ou dans l'EEE, la NITDA/NDPC au Nigeria, l'ODPC au Kenya, l'Information Regulator en Afrique du Sud, la CNDP au Maroc, la CDP au Sénégal).",
      ],
    },
    {
      id: "donnees",
      title: "2. Données que nous collectons",
      paragraphs: [
        "Nous ne collectons que les données nécessaires aux finalités décrites ci-dessous. Selon votre usage, cela peut inclure :",
      ],
      bullets: [
        "Identité et compte : nom ou prénom affiché, adresse e-mail, mot de passe (stocké sous forme hachée), type de compte (développeur, entreprise, etc.).",
        "Profil professionnel : compétences, expériences, disponibilités, CV généré, photo de profil, ville et pays renseignés, liens professionnels.",
        "Activité sur la plateforme : publications, messages, candidatures, offres, contributions Git, préférences, journaux techniques de connexion.",
        "Données techniques : adresse IP, type d'appareil et de navigateur, journaux de sécurité, cookies ou équivalents strictement nécessaires au fonctionnement et, le cas échéant, à la mesure d'audience avec votre accord.",
        "Données de paiement ou de facturation uniquement si un service payant est activé (traitées alors par un prestataire de paiement conforme).",
      ],
    },
    {
      id: "finalites",
      title: "3. Finalités et bases légales",
      paragraphs: [
        "Nous traitons vos données pour :",
      ],
      bullets: [
        "Fournir le service (compte, forum, marketplace, Hub Git) — exécution du contrat.",
        "Assurer la sécurité, prévenir la fraude et les abus — intérêt légitime et, le cas échéant, obligation légale.",
        "Améliorer le produit (statistiques agrégées, correction de bugs) — intérêt légitime, avec minimisation.",
        "Vous envoyer des e-mails transactionnels (confirmation, réinitialisation de mot de passe, notifications liées à votre activité) — exécution du contrat.",
        "Vous adresser des communications marketing uniquement avec votre consentement, que vous pouvez retirer à tout moment.",
        "Respecter nos obligations légales (conservation comptable, réponses aux autorités compétentes).",
      ],
    },
    {
      id: "conservation",
      title: "4. Durées de conservation",
      paragraphs: [
        "Nous conservons vos données seulement le temps nécessaire aux finalités :",
      ],
      bullets: [
        "Compte actif : pendant toute la durée d'utilisation du service.",
        "Après suppression du compte : suppression ou anonymisation sous 30 jours, sauf obligations légales ou litiges en cours.",
        "Journaux de sécurité : en règle générale 12 mois.",
        "Candidatures et échanges marketplace : durée de la relation puis archivage limité justifié par la preuve ou la loi applicable.",
      ],
    },
    {
      id: "partage",
      title: "5. Destinataires et sous-traitants",
      paragraphs: [
        "Vos données ne sont pas vendues. Elles peuvent être communiquées, uniquement dans la mesure nécessaire, à :",
      ],
      bullets: [
        "Nos sous-traitants techniques (hébergement, e-mail transactionnel, stockage de fichiers, outils de monitoring), liés par un contrat de traitement et des obligations de confidentialité.",
        "Les autres utilisateurs, uniquement pour les informations que vous choisissez de rendre visibles sur votre profil ou dans les espaces collaboratifs.",
        "Les autorités compétentes, lorsque la loi l'exige ou pour protéger nos droits et la sécurité des utilisateurs.",
      ],
    },
    {
      id: "transferts",
      title: "6. Transferts internationaux",
      paragraphs: [
        "DevStreet étant une plateforme panafricaine, des données peuvent être traitées dans plusieurs pays. Lorsque des données sont transférées hors de votre juridiction (EEE, Royaume-Uni ou État africain concerné), nous mettons en place des garanties appropriées : clauses contractuelles types, décisions d'adéquation lorsqu'elles existent, ou autres mécanismes reconnus par le RGPD et, le cas échéant, par le droit local (Malabo, NDPA, POPIA, etc.).",
        "Vous pouvez demander des informations sur ces garanties à privacy@devstreet.app.",
      ],
    },
    {
      id: "securite",
      title: "7. Sécurité",
      paragraphs: [
        "Nous appliquons des mesures techniques et organisationnelles adaptées : chiffrement en transit (HTTPS), hachage des mots de passe, contrôle d'accès, journaux, cloisonnement des environnements et revue des accès. Aucun système n'étant infaillible, nous vous invitons aussi à utiliser un mot de passe unique et robuste et à nous signaler tout incident suspect.",
      ],
    },
    {
      id: "droits",
      title: "8. Vos droits",
      paragraphs: [
        "Selon le droit applicable (RGPD et/ou loi nationale africaine), vous pouvez disposer des droits suivants :",
      ],
      bullets: [
        "Accès, rectification, effacement (« droit à l'oubli »).",
        "Limitation du traitement et opposition (notamment au marketing).",
        "Portabilité des données que vous nous avez fournies, lorsque le traitement repose sur le contrat ou le consentement et est automatisé.",
        "Retrait du consentement à tout moment, sans affecter la licéité du traitement antérieur.",
        "Directives relatives au sort de vos données après votre décès, lorsque le droit local le prévoit.",
      ],
    },
    {
      id: "droits-exercice",
      title: "9. Exercice des droits",
      paragraphs: [
        "Pour exercer vos droits, écrivez à privacy@devstreet.app en précisant votre demande et un moyen de vérifier votre identité. Nous répondons dans les délais prévus par la loi applicable (en principe un mois au titre du RGPD, sous réserve de complexité).",
      ],
    },
    {
      id: "mineurs",
      title: "10. Mineurs",
      paragraphs: [
        "La plateforme s'adresse à un public professionnel. Elle n'est pas destinée aux personnes de moins de 16 ans (ou de l'âge numérique de consentement applicable dans votre pays). Si vous pensez qu'un mineur a créé un compte, contactez-nous pour que nous puissions le supprimer.",
      ],
    },
    {
      id: "cookies",
      title: "11. Cookies et traceurs",
      paragraphs: [
        "Nous utilisons des cookies ou technologies similaires strictement nécessaires à l'authentification, à la sécurité et au maintien de vos préférences (langue, thème). Les traceurs non essentiels (mesure d'audience, marketing) ne sont déposés qu'avec votre consentement préalable lorsque la loi l'exige. Vous pouvez gérer vos préférences via les réglages du navigateur et, le cas échéant, le bandeau de consentement.",
      ],
    },
    {
      id: "modifications",
      title: "12. Modifications",
      paragraphs: [
        "Nous pouvons mettre à jour cette politique pour refléter l'évolution du service ou de la loi. La date de mise à jour figure en tête de page. En cas de changement substantiel, nous vous en informerons par un moyen approprié (e-mail ou notice dans le produit).",
      ],
    },
  ],
};

const TERMS_FR: LegalDocument = {
  slug: "conditions",
  title: "Conditions d'utilisation",
  updatedAt: "16 novembre 2026",
  intro:
    "Les présentes conditions régissent l'accès et l'utilisation de DevStreet (site, applications et services associés). En créant un compte ou en utilisant la plateforme, vous acceptez ces conditions.",
  disclaimer:
    "DevStreet est une plateforme de mise en relation et de collaboration technique. Elle ne se substitue pas à un contrat de travail, à un contrat de prestation ni à un conseil juridique, fiscal ou social. Les utilisateurs restent responsables de leurs engagements entre eux.",
  sections: [
    {
      id: "objet",
      title: "1. Objet du service",
      paragraphs: [
        "DevStreet propose trois espaces liés : une communauté technique (forum, chaînes, messages), une marketplace de missions et de talents, et un Hub Git pour cadrer et livrer des projets. L'objectif est de faciliter l'entraide, le recrutement et la collaboration, en priorité pour les builders africains et la diaspora.",
      ],
    },
    {
      id: "compte",
      title: "2. Compte et éligibilité",
      paragraphs: [
        "Vous devez fournir des informations exactes, maintenir la confidentialité de vos identifiants et nous informer sans délai de toute utilisation non autorisée de votre compte. Un compte est personnel ; le partage d'accès est interdit sauf fonctionnalité d'équipe expressément prévue.",
        "Vous déclarez avoir la capacité juridique de contracter et, le cas échéant, le pouvoir d'engager l'entité que vous représentez.",
      ],
    },
    {
      id: "conduite",
      title: "3. Règles de conduite",
      paragraphs: [
        "Il est interdit notamment de :",
      ],
      bullets: [
        "Publier des contenus illicites, diffamatoires, haineux, harcelants, ou portant atteinte aux droits de tiers.",
        "Usurper une identité, falsifier des compétences ou des références.",
        "Contourner les mesures de sécurité, scraper abusivement la plateforme ou perturber le service.",
        "Utiliser DevStreet pour du spam, de la tromperie ou des activités frauduleuses.",
        "Partager des secrets professionnels ou des données personnelles de tiers sans base légale.",
      ],
    },
    {
      id: "contenu",
      title: "4. Contenus utilisateurs",
      paragraphs: [
        "Vous conservez vos droits sur les contenus que vous publiez (texte, code, fichiers). Vous nous concédez une licence mondiale, non exclusive, gratuite, pour héberger, afficher et diffuser ces contenus dans le cadre du fonctionnement de la plateforme.",
        "Pour le code et les dépôts connectés via le Hub Git, les licences open source ou contractuelles que vous choisissez prévalent entre contributeurs ; DevStreet n'acquiert pas la propriété de votre code.",
      ],
    },
    {
      id: "marketplace",
      title: "5. Marketplace et relations entre utilisateurs",
      paragraphs: [
        "Les offres, candidatures, matches et échanges via la marketplace sont des relations entre utilisateurs. DevStreet n'est pas partie aux contrats conclus entre développeurs et entreprises, sauf mention contraire écrite. Chaque partie vérifie l'identité, les compétences, le droit du travail applicable et les obligations fiscales ou sociales.",
      ],
    },
    {
      id: "disponibilite",
      title: "6. Disponibilité et évolution",
      paragraphs: [
        "Nous nous efforçons d'assurer une disponibilité raisonnable du service, sans garantie d'un fonctionnement ininterrompu. Des maintenances, correctifs ou évolutions peuvent intervenir. Nous pouvons modifier, suspendre ou interrompre tout ou partie du service, en informant les utilisateurs lorsque c'est raisonnablement possible.",
      ],
    },
    {
      id: "responsabilite",
      title: "7. Responsabilité",
      paragraphs: [
        "Dans les limites autorisées par la loi applicable, DevStreet ne saurait être tenue responsable des dommages indirects, de la perte de chance, de la perte de données imputable à l'utilisateur, ou des litiges entre utilisateurs. Notre responsabilité totale, toutes causes confondues, est limitée, pour les douze derniers mois, aux sommes que vous nous avez le cas échéant versées au titre du service payant concerné, ou à un montant symbolique si le service est gratuit.",
        "Rien dans les présentes n'exclut la responsabilité en cas de dol, faute lourde, ou atteinte à l'intégrité corporelle, ni les droits irrévocables du consommateur lorsque vous agissez à ce titre.",
      ],
    },
    {
      id: "suspension",
      title: "8. Suspension et résiliation",
      paragraphs: [
        "Vous pouvez supprimer votre compte à tout moment depuis les paramètres ou en nous contactant. Nous pouvons suspendre ou résilier l'accès en cas de manquement aux présentes, de risque pour la sécurité, ou d'obligation légale, après information lorsque cela est possible.",
      ],
    },
    {
      id: "droit",
      title: "9. Droit applicable et litiges",
      paragraphs: [
        "Sous réserve de dispositions impératives plus protectrices (notamment droit de la consommation ou lois locales africaines applicables), les présentes sont régies par le droit du for de l'éditeur. En cas de litige, les parties recherchent d'abord une solution amiable. À défaut, les tribunaux compétents seront ceux du ressort du siège de l'éditeur, sauf règle impérative contraire.",
        "Si vous êtes un consommateur résidant dans l'Union européenne, vous pouvez également recourir à la plateforme européenne de règlement en ligne des litiges.",
      ],
    },
    {
      id: "contact",
      title: "10. Contact",
      paragraphs: [
        "Pour toute question sur ces conditions : contact@devstreet.app. Pour les données personnelles : privacy@devstreet.app. Voir aussi notre Politique de confidentialité.",
      ],
    },
  ],
};

const PRIVACY_EN: LegalDocument = {
  slug: "confidentialite",
  title: "Privacy Policy",
  updatedAt: "16 November 2026",
  intro:
    "DevStreet (“we”) operates a platform built first for developers and tech companies in Africa and the diaspora. This policy explains which personal data we process, why, for how long, with whom, and which rights you can exercise.",
  disclaimer:
    "This document is informed by Regulation (EU) 2016/679 (GDPR), the African Union Convention on Cyber Security and Personal Data Protection (Malabo, 2014), and principles shared across African national laws (including Nigeria’s NDPA/NDPR, Kenya’s Data Protection Act 2019, South Africa’s POPIA, Morocco’s Law 09-08, Senegal’s Law 2008-12, and frameworks in force in Burkina Faso and other ECOWAS states). It is not personalised legal advice.",
  sections: [
    {
      id: "responsable",
      title: "1. Data controller",
      paragraphs: [
        "The controller of personal data collected through DevStreet is the publisher of DevStreet. For any question about your personal data, email privacy@devstreet.app.",
        "Depending on where you use the service, a national data-protection authority may receive complaints (for example the CNIL in France/EEA, NITDA/NDPC in Nigeria, ODPC in Kenya, the Information Regulator in South Africa, CNDP in Morocco, or CDP in Senegal).",
      ],
    },
    {
      id: "donnees",
      title: "2. Data we collect",
      paragraphs: [
        "We only collect data needed for the purposes below. Depending on how you use the product, this may include:",
      ],
      bullets: [
        "Identity and account: display name, email address, password (stored hashed), account type (developer, company, etc.).",
        "Professional profile: skills, experience, availability, generated CV, profile photo, city and country, professional links.",
        "Platform activity: posts, messages, applications, offers, Git contributions, preferences, technical connection logs.",
        "Technical data: IP address, device/browser type, security logs, cookies or equivalents strictly required to run the service and, where applicable, analytics with your consent.",
        "Payment or billing data only if a paid feature is enabled (then processed by a compliant payment provider).",
      ],
    },
    {
      id: "finalites",
      title: "3. Purposes and legal bases",
      paragraphs: ["We process your data to:"],
      bullets: [
        "Provide the service (account, forum, marketplace, Git Hub) — performance of a contract.",
        "Keep the platform secure and prevent fraud or abuse — legitimate interest and, where relevant, legal obligation.",
        "Improve the product (aggregated statistics, bug fixing) — legitimate interest, with minimisation.",
        "Send transactional emails (confirmation, password reset, activity notifications) — performance of a contract.",
        "Send marketing communications only with your consent, which you may withdraw at any time.",
        "Comply with legal obligations (accounting retention, responses to competent authorities).",
      ],
    },
    {
      id: "conservation",
      title: "4. Retention",
      paragraphs: ["We keep data only as long as needed for the purposes:"],
      bullets: [
        "Active account: for as long as you use the service.",
        "After account deletion: deletion or anonymisation within 30 days, unless legal duties or ongoing disputes require otherwise.",
        "Security logs: generally 12 months.",
        "Marketplace applications and exchanges: for the relationship, then limited archiving justified by evidence or applicable law.",
      ],
    },
    {
      id: "partage",
      title: "5. Recipients and processors",
      paragraphs: [
        "We do not sell your data. It may be shared, only as needed, with:",
      ],
      bullets: [
        "Technical processors (hosting, transactional email, file storage, monitoring) bound by a processing agreement and confidentiality duties.",
        "Other users, only for information you choose to make visible on your profile or in collaborative spaces.",
        "Competent authorities when required by law or to protect our rights and users’ safety.",
      ],
    },
    {
      id: "transferts",
      title: "6. International transfers",
      paragraphs: [
        "As a pan-African platform, data may be processed in several countries. When data leaves your jurisdiction (EEA, UK or relevant African state), we use appropriate safeguards: standard contractual clauses, adequacy decisions where available, or other mechanisms recognised under the GDPR and, where applicable, local law (Malabo, NDPA, POPIA, etc.).",
        "You may request information about these safeguards at privacy@devstreet.app.",
      ],
    },
    {
      id: "securite",
      title: "7. Security",
      paragraphs: [
        "We apply appropriate technical and organisational measures: encryption in transit (HTTPS), password hashing, access control, logging, environment separation and access reviews. No system is perfect; please use a unique strong password and report any suspected incident.",
      ],
    },
    {
      id: "droits",
      title: "8. Your rights",
      paragraphs: [
        "Depending on applicable law (GDPR and/or African national law), you may have rights to:",
      ],
      bullets: [
        "Access, rectification and erasure (“right to be forgotten”).",
        "Restriction of processing and objection (including to marketing).",
        "Portability of data you provided, where processing is based on contract or consent and is automated.",
        "Withdraw consent at any time, without affecting prior lawful processing.",
        "Instructions about data after death where local law provides for it.",
      ],
    },
    {
      id: "droits-exercice",
      title: "9. How to exercise your rights",
      paragraphs: [
        "Email privacy@devstreet.app with your request and a way to verify your identity. We respond within the timelines set by applicable law (generally one month under the GDPR, subject to complexity).",
      ],
    },
    {
      id: "mineurs",
      title: "10. Minors",
      paragraphs: [
        "The platform is aimed at professionals. It is not intended for people under 16 (or the digital age of consent in your country). If you believe a minor created an account, contact us so we can delete it.",
      ],
    },
    {
      id: "cookies",
      title: "11. Cookies and similar technologies",
      paragraphs: [
        "We use cookies or similar technologies strictly necessary for authentication, security and preferences (language, theme). Non-essential trackers (analytics, marketing) are set only with prior consent where required. You can manage preferences in your browser and, where shown, via a consent banner.",
      ],
    },
    {
      id: "modifications",
      title: "12. Changes",
      paragraphs: [
        "We may update this policy to reflect product or legal changes. The update date appears at the top. For material changes, we will notify you by an appropriate means (email or in-product notice).",
      ],
    },
  ],
};

const TERMS_EN: LegalDocument = {
  slug: "conditions",
  title: "Terms of Use",
  updatedAt: "16 November 2026",
  intro:
    "These terms govern access to and use of DevStreet (website, apps and related services). By creating an account or using the platform, you agree to these terms.",
  disclaimer:
    "DevStreet is a technical networking and collaboration platform. It does not replace an employment contract, a service agreement, or legal, tax or social advice. Users remain responsible for their commitments to each other.",
  sections: [
    {
      id: "objet",
      title: "1. Service",
      paragraphs: [
        "DevStreet offers three linked spaces: a technical community (forum, channels, messaging), a marketplace for missions and talent, and a Git Hub to frame and ship projects. The goal is to make peer help, hiring and collaboration easier—first for African builders and the diaspora.",
      ],
    },
    {
      id: "compte",
      title: "2. Account and eligibility",
      paragraphs: [
        "You must provide accurate information, keep your credentials confidential and notify us promptly of any unauthorised use of your account. Accounts are personal; sharing access is forbidden unless an explicit team feature allows it.",
        "You represent that you have legal capacity to contract and, where relevant, authority to bind the entity you represent.",
      ],
    },
    {
      id: "conduite",
      title: "3. Acceptable use",
      paragraphs: ["You must not, among other things:"],
      bullets: [
        "Post unlawful, defamatory, hateful or harassing content, or content that infringes third-party rights.",
        "Impersonate others or falsify skills or references.",
        "Bypass security, scrape the platform abusively or disrupt the service.",
        "Use DevStreet for spam, deception or fraud.",
        "Share trade secrets or third-party personal data without a lawful basis.",
      ],
    },
    {
      id: "contenu",
      title: "4. User content",
      paragraphs: [
        "You keep your rights in content you post (text, code, files). You grant us a worldwide, non-exclusive, royalty-free licence to host, display and distribute that content as needed to operate the platform.",
        "For code and repositories connected via the Git Hub, the open-source or contractual licences you choose govern between contributors; DevStreet does not take ownership of your code.",
      ],
    },
    {
      id: "marketplace",
      title: "5. Marketplace and user relationships",
      paragraphs: [
        "Offers, applications, matches and marketplace exchanges are relationships between users. Unless we state otherwise in writing, DevStreet is not a party to contracts between developers and companies. Each party must verify identity, skills, applicable labour law and tax or social obligations.",
      ],
    },
    {
      id: "disponibilite",
      title: "6. Availability and changes",
      paragraphs: [
        "We aim for reasonable availability without guaranteeing uninterrupted operation. Maintenance, fixes or product changes may occur. We may modify, suspend or discontinue all or part of the service, notifying users when reasonably possible.",
      ],
    },
    {
      id: "responsabilite",
      title: "7. Liability",
      paragraphs: [
        "To the extent permitted by applicable law, DevStreet is not liable for indirect damages, loss of opportunity, data loss caused by the user, or disputes between users. Our aggregate liability for the preceding twelve months is limited to amounts you paid us for the relevant paid service, or a symbolic amount if the service is free.",
        "Nothing excludes liability for fraud, gross negligence, or personal injury, nor irrevocable consumer rights where you act as a consumer.",
      ],
    },
    {
      id: "suspension",
      title: "8. Suspension and termination",
      paragraphs: [
        "You may delete your account at any time from settings or by contacting us. We may suspend or terminate access for breach of these terms, security risk, or legal obligation, after notice where possible.",
      ],
    },
    {
      id: "droit",
      title: "9. Governing law and disputes",
      paragraphs: [
        "Subject to more protective mandatory rules (including consumer law or applicable African local law), these terms are governed by the law of the publisher’s forum. Parties will first seek an amicable solution. Failing that, courts of the publisher’s registered office have jurisdiction, unless mandatory rules say otherwise.",
        "If you are a consumer in the European Union, you may also use the European Online Dispute Resolution platform.",
      ],
    },
    {
      id: "contact",
      title: "10. Contact",
      paragraphs: [
        "Questions about these terms: contact@devstreet.app. Personal data: privacy@devstreet.app. See also our Privacy Policy.",
      ],
    },
  ],
};

export function getLegalDocument(
  slug: LegalDocument["slug"],
  language: string
): LegalDocument {
  const en = language.toLowerCase().startsWith("en");
  if (slug === "confidentialite") return en ? PRIVACY_EN : PRIVACY_FR;
  return en ? TERMS_EN : TERMS_FR;
}
