import { useState } from "react";
import { Button } from "@/components/ui/button";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import {
  Briefcase,
  Check,
  CheckCircle2,
  Code2,
  FileDown,
  FolderGit2,
  GitBranch,
  GitPullRequest,
  Hash,
  Lock,
  MessageSquare,
  Mic,
  Sparkles,
  Terminal,
  Users,
} from "lucide-react";
import { Link } from "react-router-dom";

type PreviewTab = "forum" | "marketplace" | "hub";

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState<PreviewTab>("forum");

  return (
    <div className="min-h-svh bg-background text-foreground">
      {/* Navigation sobre */}
      <header className="sticky top-0 z-30 border-b border-border/70 bg-background/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-8">
            <Link
              to="/welcome"
              className="flex items-center gap-2.5"
              aria-label="DevStreet — accueil"
            >
              <span className="flex size-8 items-center justify-center rounded-lg bg-brand text-brand-foreground">
                <Terminal className="size-4" aria-hidden />
              </span>
              <span className="text-base font-bold tracking-tight">
                DevStreet
              </span>
            </Link>

            <nav
              aria-label="Découvrir DevStreet"
              className="hidden items-center gap-7 text-sm font-medium text-muted-foreground md:flex"
            >
              <a href="#entraide" className="hover:text-foreground">
                Communauté
              </a>
              <a href="#missions" className="hover:text-foreground">
                Marketplace
              </a>
              <a href="#projets" className="hover:text-foreground">
                Hub Git
              </a>
            </nav>
          </div>

          <div className="flex items-center gap-2">
            <LanguageToggle />
            <ModeToggle />
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="hidden sm:inline-flex"
            >
              <Link to="/login">Connexion</Link>
            </Button>
            <Button
              asChild
              size="sm"
              className="bg-brand text-brand-foreground hover:bg-brand/90"
            >
              <Link to="/login?mode=register">Rejoindre DevStreet</Link>
            </Button>
          </div>
        </div>
      </header>

      <main>
        {/* HERO : Titre fort + Aperçu réel de la plateforme */}
        <section className="relative overflow-hidden pt-12 pb-20 sm:pt-20 sm:pb-28">
          {/* Halo de teinte très discret, purement statique */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[420px] bg-gradient-to-b from-brand-soft/70 via-brand-soft/20 to-transparent"
          />

          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-brand-soft-border bg-brand-soft px-3.5 py-1 text-xs font-medium text-brand">
                <span className="size-1.5 rounded-full bg-brand" />
                Un seul compte pour le forum, les missions et vos projets Git
              </div>

              <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-6xl sm:leading-[1.06]">
                Discutez code.
                <br />
                Décrochez vos missions.
                <br />
                <span className="text-brand">Livrez à plusieurs.</span>
              </h1>

              <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
                Là où vos échanges techniques, votre profil pro vérifiable et vos
                contributions sur de vrais dépôts vivent enfin au même endroit.
              </p>

              <div className="mt-7 flex flex-wrap items-center gap-3">
                <Button
                  asChild
                  size="lg"
                  className="h-12 bg-brand px-7 text-brand-foreground hover:bg-brand/90"
                >
                  <Link to="/login?mode=register">Créer mon compte</Link>
                </Button>
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                  className="h-12 px-6"
                >
                  <Link to="/login">J&apos;ai déjà un compte</Link>
                </Button>
              </div>
            </div>

            {/* GRANDE FENÊTRE D'APERÇU PRODUIT (statique, explorable au clic) */}
            <div className="mt-12 overflow-hidden rounded-2xl border border-border bg-card shadow-card-hover">
              {/* Barre supérieure de fenêtre + onglets des 3 espaces */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-muted/50 px-4 py-3 sm:px-6">
                <div className="flex items-center gap-2">
                  <span className="size-2.5 rounded-full bg-border" />
                  <span className="size-2.5 rounded-full bg-border" />
                  <span className="size-2.5 rounded-full bg-border" />
                  <span className="ml-2 text-xs font-medium text-muted-foreground">
                    devstreet.app
                  </span>
                </div>

                <div
                  role="tablist"
                  aria-label="Aperçu des espaces DevStreet"
                  className="flex items-center gap-1 rounded-lg border border-border bg-background p-1"
                >
                  <button
                    type="button"
                    role="tab"
                    aria-selected={activeTab === "forum"}
                    onClick={() => setActiveTab("forum")}
                    className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
                      activeTab === "forum"
                        ? "bg-brand text-brand-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <MessageSquare className="size-3.5" aria-hidden />
                    Forum & Communautés
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={activeTab === "marketplace"}
                    onClick={() => setActiveTab("marketplace")}
                    className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
                      activeTab === "marketplace"
                        ? "bg-brand text-brand-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <Briefcase className="size-3.5" aria-hidden />
                    Marketplace
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={activeTab === "hub"}
                    onClick={() => setActiveTab("hub")}
                    className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
                      activeTab === "hub"
                        ? "bg-brand text-brand-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <FolderGit2 className="size-3.5" aria-hidden />
                    DevStreet Hub
                  </button>
                </div>
              </div>

              {/* Corps de la fenêtre simulée */}
              <div className="grid md:grid-cols-12">
                {/* Mini sidebar fidèle au produit */}
                <aside className="hidden border-r border-border bg-muted/20 p-4 md:col-span-3 md:block">
                  <p className="px-2 text-[11px] font-semibold text-muted-foreground">
                    Espaces
                  </p>
                  <div className="mt-2 space-y-1 text-xs">
                    <div
                      className={`flex items-center justify-between rounded-lg px-2.5 py-2 font-medium ${
                        activeTab === "forum"
                          ? "bg-brand-soft text-brand"
                          : "text-muted-foreground"
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <Hash className="size-3.5" />
                        backend-python
                      </span>
                      <span className="rounded-full bg-brand px-1.5 py-0.5 text-[10px] text-brand-foreground">
                        12
                      </span>
                    </div>
                    <div
                      className={`flex items-center justify-between rounded-lg px-2.5 py-2 font-medium ${
                        activeTab === "marketplace"
                          ? "bg-brand-soft text-brand"
                          : "text-muted-foreground"
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <Briefcase className="size-3.5" />
                        Offres pour moi
                      </span>
                      <span className="text-[11px] font-semibold text-success">
                        94%
                      </span>
                    </div>
                    <div
                      className={`flex items-center justify-between rounded-lg px-2.5 py-2 font-medium ${
                        activeTab === "hub"
                          ? "bg-brand-soft text-brand"
                          : "text-muted-foreground"
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <GitBranch className="size-3.5" />
                        api-gateway-oss
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        4 tâches
                      </span>
                    </div>
                  </div>

                  <div className="mt-6 border-t border-border pt-4">
                    <p className="px-2 text-[11px] font-semibold text-muted-foreground">
                      Messages directs
                    </p>
                    <div className="mt-2 space-y-2 px-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="size-2 rounded-full bg-success" />
                        <span className="truncate">@sarah.dev</span>
                        <Mic className="ml-auto size-3 text-muted-foreground" />
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <span className="size-2 rounded-full bg-border" />
                        <span className="truncate">@karim_ops</span>
                      </div>
                    </div>
                  </div>
                </aside>

                {/* Contenu dynamique selon l'onglet choisi */}
                <div className="p-5 sm:p-7 md:col-span-9">
                  {activeTab === "forum" && (
                    <div className="space-y-5">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="rounded-md bg-brand-soft px-2.5 py-1 text-xs font-semibold text-brand">
                            Entraide
                          </span>
                          <span className="text-xs text-muted-foreground">
                            dans #backend-python · il y a 18 min
                          </span>
                        </div>
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-success/15 px-3 py-1 text-xs font-semibold text-success">
                          <CheckCircle2 className="size-3.5" />
                          Aide confirmée
                        </span>
                      </div>

                      <div>
                        <h3 className="text-lg font-semibold">
                          Verrouillage optimiste ou select_for_update sur la réservation de créneaux ?
                        </h3>
                        <p className="mt-1.5 text-sm text-muted-foreground">
                          Sur PostgreSQL avec 200 requêtes concurrentes, on hésite entre un numéro de version et un lock ligne dans le repository.
                        </p>
                      </div>

                      <div className="rounded-xl border border-border bg-muted/60 p-4 text-xs">
                        <div className="flex items-center justify-between text-muted-foreground">
                          <span className="font-semibold text-foreground">
                            @nadia_db · Réponse retenue
                          </span>
                          <span>PostgreSQL · Django</span>
                        </div>
                        <pre className="mt-2.5 overflow-x-auto rounded-lg bg-background p-3 text-xs leading-relaxed text-foreground">
                          <code>{`Slot.objects.select_for_update(skip_locked=True).filter(is_free=True).first()`}</code>
                        </pre>
                      </div>
                    </div>
                  )}

                  {activeTab === "marketplace" && (
                    <div className="grid gap-6 sm:grid-cols-2">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-semibold">Yanis M. · Backend Senior</p>
                            <p className="text-xs text-success font-medium">
                              ● Disponible dès le 18 nov.
                            </p>
                          </div>
                          <span className="inline-flex items-center gap-1 rounded-lg border border-border bg-muted/50 px-2.5 py-1 text-xs font-medium">
                            <FileDown className="size-3.5" />
                            CV PDF
                          </span>
                        </div>

                        <div className="space-y-2.5 pt-1">
                          <div>
                            <div className="flex justify-between text-xs">
                              <span className="font-medium">Python / Django REST</span>
                              <span className="text-muted-foreground">Expert · 6 ans</span>
                            </div>
                            <div className="mt-1 h-2 rounded-full bg-muted">
                              <div className="h-2 w-[92%] rounded-full bg-brand" />
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-xs">
                              <span className="font-medium">PostgreSQL & Redis</span>
                              <span className="text-muted-foreground">Avancé · 4 ans</span>
                            </div>
                            <div className="mt-1 h-2 rounded-full bg-muted">
                              <div className="h-2 w-[78%] rounded-full bg-brand" />
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-xs">
                              <span className="font-medium">TypeScript / React</span>
                              <span className="text-muted-foreground">Confirmé · 3 ans</span>
                            </div>
                            <div className="mt-1 h-2 rounded-full bg-muted">
                              <div className="h-2 w-[64%] rounded-full bg-brand" />
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col justify-between rounded-xl border border-brand-soft-border bg-brand-soft/60 p-4">
                        <div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-brand">
                              Offre compatible
                            </span>
                            <span className="rounded-full bg-brand px-2.5 py-0.5 text-xs font-bold text-brand-foreground">
                              94 % match
                            </span>
                          </div>
                          <p className="mt-3 text-base font-semibold">
                            Lead API Django · Fintech
                          </p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            Télétravail · Mission 6 mois ou CDI · Démarrage immédiat
                          </p>
                        </div>

                        <div className="mt-4 flex flex-wrap gap-1.5 border-t border-brand-soft-border/60 pt-3 text-[11px]">
                          <span className="rounded bg-background px-2 py-0.5 font-medium">
                            Stack alignée 5/5
                          </span>
                          <span className="rounded bg-background px-2 py-0.5 font-medium">
                            Créneau dispo OK
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "hub" && (
                    <div className="space-y-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <h3 className="text-base font-semibold">
                            api-gateway-oss · Passerelle d&apos;authentification
                          </h3>
                          <p className="text-xs text-muted-foreground">
                            Dépôt Git connecté · 7 contributeurs actifs
                          </p>
                        </div>
                        <span className="inline-flex items-center gap-1.5 rounded-lg bg-brand-soft px-3 py-1 text-xs font-semibold text-brand">
                          <Sparkles className="size-3.5" />
                          Atelier IA activé
                        </span>
                      </div>

                      <div className="divide-y divide-border rounded-xl border border-border bg-background">
                        <div className="flex items-center justify-between px-4 py-3 text-xs">
                          <div className="flex items-center gap-2.5">
                            <GitPullRequest className="size-4 text-success" />
                            <span className="font-medium">
                              Rotation des clés JWT sans coupure
                            </span>
                          </div>
                          <span className="rounded-full bg-success/15 px-2.5 py-0.5 font-semibold text-success">
                            Validée
                          </span>
                        </div>
                        <div className="flex items-center justify-between px-4 py-3 text-xs">
                          <div className="flex items-center gap-2.5">
                            <Code2 className="size-4 text-info" />
                            <span className="font-medium">
                              Tests de charge sur le rate-limiter Redis
                            </span>
                          </div>
                          <span className="rounded-full bg-info/15 px-2.5 py-0.5 font-semibold text-info">
                            En revue
                          </span>
                        </div>
                        <div className="flex items-center justify-between px-4 py-3 text-xs">
                          <div className="flex items-center gap-2.5">
                            <FolderGit2 className="size-4 text-warning" />
                            <span className="font-medium">
                              Export OpenAPI 3.1 des webhooks
                            </span>
                          </div>
                          <span className="rounded-full bg-warning-soft px-2.5 py-0.5 font-semibold text-warning">
                            Ouverte à contribution
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SCÈNE 1 — COMMUNAUTÉ (Texte court à gauche / Composition visuelle à droite) */}
        <section id="entraide" className="border-t border-border py-20 sm:py-24">
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-12">
            <div className="lg:col-span-5">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Des échanges techniques qui aboutissent vraiment.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                Fini les serveurs bruyants où les bonnes réponses disparaissent en dix minutes.
              </p>

              <ul className="mt-7 space-y-4 text-sm">
                <li className="flex items-start gap-3">
                  <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-brand-soft text-brand">
                    <Check className="size-3" />
                  </span>
                  <span>
                    <strong>Formats adaptés</strong> : entraide avec validation, sondages d&apos;architecture, vitrines de projets.
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-brand-soft text-brand">
                    <Check className="size-3" />
                  </span>
                  <span>
                    <strong>Communautés publiques ou privées</strong> sur lien d&apos;invitation, avec salons et rôles dédiés.
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-brand-soft text-brand">
                    <Check className="size-3" />
                  </span>
                  <span>
                    <strong>Messages vocaux, pièces jointes et résumé quotidien</strong> pour ne rien rater sans être dérangé.
                  </span>
                </li>
              </ul>
            </div>

            {/* Visuel expressif empilé (pas des cards de texte) */}
            <div className="space-y-3 lg:col-span-7">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/60 px-3 py-1.5 text-xs font-medium">
                  <Hash className="size-3.5 text-brand" />
                  architecture-clean
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/60 px-3 py-1.5 text-xs font-medium">
                  <Lock className="size-3.5 text-muted-foreground" />
                  core-maintainers (sur invitation)
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-brand-soft-border bg-brand-soft px-3 py-1.5 text-xs font-semibold text-brand">
                  <Users className="size-3.5" />
                  Chaînes thématiques
                </span>
              </div>

              <div className="rounded-2xl border border-border bg-muted/30 p-6">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span className="font-semibold text-foreground">
                    Sondage technique · 84 votes
                  </span>
                  <span>Clôturé</span>
                </div>
                <p className="mt-2 text-base font-semibold">
                  Quelle stratégie de cache utilisez-vous devant vos ViewSets DRF ?
                </p>

                <div className="mt-4 space-y-2.5 text-xs">
                  <div className="relative overflow-hidden rounded-lg border border-brand-soft-border bg-background p-2.5">
                    <div
                      aria-hidden
                      className="absolute inset-y-0 left-0 w-[58%] bg-brand-soft"
                    />
                    <div className="relative flex justify-between font-medium">
                      <span>Invalidation ciblée au niveau Service + Redis</span>
                      <span className="font-bold text-brand">58 %</span>
                    </div>
                  </div>
                  <div className="relative overflow-hidden rounded-lg border border-border bg-background p-2.5">
                    <div
                      aria-hidden
                      className="absolute inset-y-0 left-0 w-[29%] bg-muted"
                    />
                    <div className="relative flex justify-between">
                      <span>Cache HTTP court (30s) par endpoint</span>
                      <span className="text-muted-foreground">29 %</span>
                    </div>
                  </div>
                  <div className="relative overflow-hidden rounded-lg border border-border bg-background p-2.5">
                    <div
                      aria-hidden
                      className="absolute inset-y-0 left-0 w-[13%] bg-muted"
                    />
                    <div className="relative flex justify-between">
                      <span>Pas de cache applicatif</span>
                      <span className="text-muted-foreground">13 %</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SCÈNE 2 — MARKETPLACE (Visuel à gauche / Texte court à droite, fond contrasté) */}
        <section
          id="missions"
          className="border-t border-border bg-muted/35 py-20 sm:py-24"
        >
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-12">
            {/* Composition visuelle : Calendrier dispo + Score + CV */}
            <div className="order-2 lg:order-1 lg:col-span-7">
              <div className="overflow-hidden rounded-2xl border border-border bg-background">
                <div className="flex items-center justify-between border-b border-border px-6 py-4">
                  <div>
                    <p className="text-base font-bold">Profil professionnel & Matching</p>
                    <p className="text-xs text-muted-foreground">
                      Visible uniquement selon vos règles de confidentialité
                    </p>
                  </div>
                  <span className="rounded-lg bg-brand px-3 py-1.5 text-xs font-semibold text-brand-foreground">
                    CV généré en 1 clic
                  </span>
                </div>

                <div className="divide-y divide-border px-6">
                  <div className="flex items-center justify-between py-4">
                    <div>
                      <p className="text-sm font-semibold">Compétences pondérées</p>
                      <p className="text-xs text-muted-foreground">
                        Niveau réel + années d&apos;expérience vérifiables
                      </p>
                    </div>
                    <div className="flex gap-1.5 text-xs font-semibold">
                      <span className="rounded-md bg-brand-soft px-2.5 py-1 text-brand">
                        Django · 5 ans
                      </span>
                      <span className="rounded-md bg-brand-soft px-2.5 py-1 text-brand">
                        React · 4 ans
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between py-4">
                    <div>
                      <p className="text-sm font-semibold">Disponibilités à jour</p>
                      <p className="text-xs text-muted-foreground">
                        Fini les messages pour des postes qui ne collent pas à votre agenda
                      </p>
                    </div>
                    <span className="rounded-full bg-success/15 px-3 py-1 text-xs font-semibold text-success">
                      Temps plein · Dès maintenant
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-4">
                    <div>
                      <p className="text-sm font-semibold">Côté recruteur : vivier & offres</p>
                      <p className="text-xs text-muted-foreground">
                        Candidatures triées automatiquement selon les prérequis techniques
                      </p>
                    </div>
                    <span className="text-lg font-bold text-brand">92 %</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="order-1 lg:order-2 lg:col-span-5">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Votre profil parle avec des preuves, pas des mots-clés.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                Que vous cherchiez une mission freelance, un CDI ou un renfort technique pour votre équipe, le matching repose sur la stack exacte et la disponibilité réelle.
              </p>

              <div className="mt-8 flex items-baseline gap-8 border-t border-border pt-6">
                <div>
                  <p className="text-2xl font-bold text-brand">PDF</p>
                  <p className="text-xs text-muted-foreground">
                    CV toujours propre et à jour
                  </p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-brand">Direct</p>
                  <p className="text-xs text-muted-foreground">
                    Échange sans intermédiaire
                  </p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-brand">3 niveaux</p>
                  <p className="text-xs text-muted-foreground">
                    Public, recruteurs ou privé
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SCÈNE 3 — DEVSTREET HUB (Flux visuel horizontal sans boîtes lourdes) */}
        <section id="projets" className="border-t border-border py-20 sm:py-24">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="grid gap-8 lg:grid-cols-12 lg:items-end">
              <div className="lg:col-span-7">
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                  Du ticket ouvert au code fusionné dans DevStreet Hub.
                </h2>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground lg:col-span-5">
                Lancez un projet open-source ou d&apos;équipe, découpez les tâches, reliez votre dépôt Git et validez chaque contribution avec l&apos;appui de l&apos;atelier IA.
              </p>
            </div>

            {/* Frise de flux continue au lieu de cartes séparées */}
            <div className="mt-12 grid divide-y divide-border overflow-hidden rounded-2xl border border-border bg-muted/20 md:grid-cols-4 md:divide-x md:divide-y-0">
              <div className="p-6">
                <FolderGit2 className="size-5 text-brand" />
                <p className="mt-4 text-sm font-bold">Cadrage du projet</p>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
                  Objectif, stack, rôles des membres et connexion à votre forge Git.
                </p>
              </div>
              <div className="p-6">
                <Code2 className="size-5 text-brand" />
                <p className="mt-4 text-sm font-bold">Tâches ouvertes</p>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
                  Les contributeurs prennent un ticket clair avec critères attendus.
                </p>
              </div>
              <div className="p-6">
                <Sparkles className="size-5 text-brand" />
                <p className="mt-4 text-sm font-bold">Atelier IA intégré</p>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
                  Exploration rapide du code existant avec quotas maîtrisés par projet.
                </p>
              </div>
              <div className="p-6">
                <GitPullRequest className="size-5 text-success" />
                <p className="mt-4 text-sm font-bold">Revue & validation</p>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
                  Retour des mainteneurs et historique de contribution visible sur votre profil.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* BLOC EXPRESSIF PLEIN-TON BRAND (casse radicalement le fond blanc) */}
        <section className="px-4 pb-20 sm:px-6">
          <div className="mx-auto max-w-6xl rounded-3xl bg-brand px-6 py-14 text-brand-foreground sm:px-12 sm:py-16">
            <div className="grid gap-10 lg:grid-cols-12 lg:items-center">
              <div className="lg:col-span-7">
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                  Construisez votre réseau par ce que vous savez faire.
                </h2>
                <div className="mt-8 grid gap-6 border-t border-brand-foreground/20 pt-6 sm:grid-cols-3">
                  <div>
                    <p className="text-sm font-bold">Développeurs</p>
                    <p className="mt-1 text-xs leading-relaxed text-brand-foreground/80">
                      Entraide pointue, CV auto et missions ciblées.
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-bold">Recruteurs</p>
                    <p className="mt-1 text-xs leading-relaxed text-brand-foreground/80">
                      Profils disponibles, stack vérifiée, zéro bruit.
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-bold">Mainteneurs</p>
                    <p className="mt-1 text-xs leading-relaxed text-brand-foreground/80">
                      Communauté, tickets Git et contributeurs motivés.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex flex-col items-start gap-3 lg:col-span-5 lg:items-end">
                <Button
                  asChild
                  size="lg"
                  className="h-12 bg-background px-8 font-semibold text-foreground hover:bg-background/90"
                >
                  <Link to="/login?mode=register">Créer mon compte gratuitement</Link>
                </Button>
                <Link
                  to="/login"
                  className="text-xs font-medium text-brand-foreground/80 underline-offset-4 hover:text-brand-foreground hover:underline"
                >
                  Déjà inscrit ? Se connecter à mon espace
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-border py-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="flex items-center gap-2 font-medium text-foreground">
            <span className="flex size-5 items-center justify-center rounded bg-brand text-brand-foreground">
              <Terminal className="size-3" aria-hidden />
            </span>
            DevStreet
          </div>
          <div className="flex flex-wrap gap-6">
            <a href="#entraide" className="hover:text-foreground">
              Communauté
            </a>
            <a href="#missions" className="hover:text-foreground">
              Marketplace
            </a>
            <a href="#projets" className="hover:text-foreground">
              Hub Git
            </a>
            <Link to="/login" className="hover:text-foreground">
              Connexion
            </Link>
            <Link to="/login?mode=register" className="hover:text-foreground">
              Inscription
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
