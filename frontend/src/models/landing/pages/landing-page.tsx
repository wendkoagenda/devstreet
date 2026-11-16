import {
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { BrandLogo } from "@/components/brand/brand-logo";
import { Button } from "@/components/ui/button";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  Briefcase,
  Check,
  FolderGit2,
  GitPullRequest,
  Hash,
  MessageSquare,
  Sparkles,
  Users,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { GlobalCommunitySection } from "../components/global-community-section";
import { ProfilesMarquee } from "../components/profiles-marquee";

const STATS = [
  { value: "3", labelKey: "landing.stat_spaces" },
  { value: "1", labelKey: "landing.stat_account" },
  { value: "CV", labelKey: "landing.stat_cv" },
  { value: "Git", labelKey: "landing.stat_git" },
] as const;

type FeatureCard = {
  id: string;
  labelKey: string;
  titleKey: string;
  bodyKey: string;
  ctaKey: string;
  href: string;
  panelClass: string;
  gridClass: string;
  reverse?: boolean;
  visual: ReactNode;
  icon: ReactNode;
};

const FEATURES: FeatureCard[] = [
  {
    id: "communauté",
    labelKey: "landing.features.community_label",
    titleKey: "landing.features.community_title",
    bodyKey: "landing.features.community_body",
    ctaKey: "landing.features.community_cta",
    href: "/login?mode=register",
    panelClass:
      "bg-[hsl(160_28%_94%)] dark:bg-[hsl(160_18%_14%)]",
    gridClass:
      "bg-[linear-gradient(to_right,hsl(var(--foreground)/0.04)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--foreground)/0.04)_1px,transparent_1px)]",
    icon: <MessageSquare className="size-6" aria-hidden />,
    visual: (
      <>
        <OrbitPill className="left-[12%] top-[18%]">
          <Hash className="size-3.5 text-brand" />
          backend-python
        </OrbitPill>
        <OrbitPill className="right-[10%] top-[28%]">
          <Users className="size-3.5 text-brand" />
          core-maintainers
        </OrbitPill>
        <OrbitPill className="left-[18%] bottom-[28%]">
          <MessageSquare className="size-3.5 text-brand" />
          Aide confirmée
        </OrbitPill>
        <OrbitPill className="right-[14%] bottom-[18%]">
          <Check className="size-3.5 text-success" />
          Réponse retenue
        </OrbitPill>
      </>
    ),
  },
  {
    id: "marketplace",
    labelKey: "landing.features.marketplace_label",
    titleKey: "landing.features.marketplace_title",
    bodyKey: "landing.features.marketplace_body",
    ctaKey: "landing.features.marketplace_cta",
    href: "/login?mode=register",
    panelClass: "bg-brand-soft",
    gridClass:
      "bg-[linear-gradient(to_right,hsl(var(--brand)/0.08)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--brand)/0.08)_1px,transparent_1px)]",
    reverse: true,
    icon: <Briefcase className="size-6" aria-hidden />,
    visual: (
      <>
        <OrbitPill className="left-[10%] top-[20%]">
          <Briefcase className="size-3.5 text-brand" />
          Django · 5 ans
        </OrbitPill>
        <OrbitPill className="right-[8%] top-[32%]">React · 4 ans</OrbitPill>
        <OrbitPill className="left-[16%] bottom-[30%]">
          <span className="font-semibold text-brand">94 %</span>
          match
        </OrbitPill>
        <OrbitPill className="right-[12%] bottom-[16%]">
          Disponible · maintenant
        </OrbitPill>
      </>
    ),
  },
  {
    id: "hub",
    labelKey: "landing.features.hub_label",
    titleKey: "landing.features.hub_title",
    bodyKey: "landing.features.hub_body",
    ctaKey: "landing.features.hub_cta",
    href: "/login?mode=register",
    panelClass:
      "bg-[hsl(210_40%_94%)] dark:bg-[hsl(210_20%_14%)]",
    gridClass:
      "bg-[linear-gradient(to_right,hsl(var(--foreground)/0.04)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--foreground)/0.04)_1px,transparent_1px)]",
    icon: <FolderGit2 className="size-6" aria-hidden />,
    visual: (
      <>
        <OrbitPill className="left-[12%] top-[18%]">
          <FolderGit2 className="size-3.5 text-brand" />
          api-gateway-oss
        </OrbitPill>
        <OrbitPill className="right-[10%] top-[30%]">
          <GitPullRequest className="size-3.5 text-success" />
          PR validée
        </OrbitPill>
        <OrbitPill className="left-[18%] bottom-[28%]">
          <Sparkles className="size-3.5 text-brand" />
          Atelier IA
        </OrbitPill>
        <OrbitPill className="right-[14%] bottom-[16%]">
          4 tâches ouvertes
        </OrbitPill>
      </>
    ),
  },
];

export default function LandingPage() {
  const { t } = useTranslation();
  return (
    <div id="top" className="min-h-svh bg-background text-foreground">
      <header className="sticky top-0 z-40 bg-background/85 backdrop-blur-md">
        <div className="mx-auto flex h-[4.25rem] max-w-6xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-10">
            <Link
              to="/welcome"
              className="flex items-center"
              aria-label={t("landing.home_aria")}
            >
              <BrandLogo className="h-8" />
            </Link>

            <nav
              aria-label={t("landing.nav_aria")}
              className="hidden items-center gap-8 text-[0.9375rem] font-medium text-muted-foreground md:flex"
            >
              <a
                href="#produit"
                className="transition-colors hover:text-foreground"
              >
                {t("landing.nav_product")}
              </a>
              <a
                href="#communauté"
                className="transition-colors hover:text-foreground"
              >
                {t("landing.nav_community")}
              </a>
              <a
                href="#marketplace"
                className="transition-colors hover:text-foreground"
              >
                {t("landing.nav_marketplace")}
              </a>
              <a
                href="#hub"
                className="transition-colors hover:text-foreground"
              >
                {t("landing.nav_hub")}
              </a>
            </nav>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2">
            <LanguageToggle />
            <ModeToggle />
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="hidden text-[0.9375rem] font-medium sm:inline-flex"
            >
              <Link to="/login">{t("landing.login")}</Link>
            </Button>
            <Button
              asChild
              size="sm"
              className="h-10 rounded-xl bg-foreground px-4 text-background hover:bg-foreground/90"
            >
              <Link to="/login?mode=register">{t("landing.create_account")}</Link>
            </Button>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden pb-16 pt-14 sm:pb-24 sm:pt-20">
          <div className="relative z-10 mx-auto max-w-4xl px-4 text-center sm:px-6">
            <p className="inline-flex items-center rounded-full bg-foreground px-3.5 py-1.5 text-xs font-semibold text-background">
              {t("landing.badge")}
            </p>

            <h1 className="mt-7 text-[2.35rem] font-bold leading-[1.08] tracking-tight sm:text-6xl sm:leading-[1.05]">
              {t("landing.hero_line1")}
              <br />
              {t("landing.hero_line2")}
              <br />
              <span className="text-brand">{t("landing.hero_line3")}</span>
            </h1>

            <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
              {t("landing.hero_sub")}
            </p>

            <div className="mt-9 flex flex-wrap items-center justify-center gap-x-6 gap-y-3">
              <Button
                asChild
                size="lg"
                className="h-12 rounded-xl bg-foreground px-7 text-background hover:bg-foreground/90"
              >
                <Link to="/login?mode=register">{t("landing.create_account")}</Link>
              </Button>
              <Link
                to="/login"
                className="text-[0.9375rem] font-medium text-foreground underline-offset-4 transition-colors hover:underline"
              >
                {t("landing.have_account")}
              </Link>
            </div>

            <div className="mx-auto mt-14 grid max-w-3xl grid-cols-2 gap-y-8 sm:grid-cols-4 sm:gap-0">
              {STATS.map((stat, i) => (
                <div
                  key={stat.labelKey}
                  className={`flex flex-col items-center px-2 sm:px-4 ${
                    i > 0 ? "sm:border-l sm:border-border" : ""
                  }`}
                >
                  <span className="text-2xl font-bold tracking-tight sm:text-3xl">
                    {stat.value}
                  </span>
                  <span className="mt-1 text-xs text-muted-foreground sm:text-sm">
                    {t(stat.labelKey)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 bottom-0 h-[42%] bg-[radial-gradient(ellipse_at_50%_100%,hsl(var(--brand)/0.22)_0%,hsl(160_40%_70%/0.12)_42%,transparent_72%)]"
          />
        </section>

        <ProfilesMarquee />

        <section
          id="produit"
          className="scroll-mt-24 pb-6 pt-4 sm:pb-10 sm:pt-8"
        >
          <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 sm:px-6 lg:flex-row lg:items-end lg:justify-between lg:gap-16">
            <div className="flex max-w-2xl gap-3">
              <span
                aria-hidden
                className="mt-1.5 h-8 w-1 shrink-0 rounded-full bg-brand"
              />
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl sm:leading-tight">
                {t("landing.product_title")}
              </h2>
            </div>
            <p className="max-w-md text-sm leading-relaxed text-muted-foreground lg:pb-1 lg:text-right">
              {t("landing.product_sub")}
            </p>
          </div>
        </section>

        <FeatureStack />

        <GlobalCommunitySection />
      </main>

      {/* CTA clair (coins bas arrondis) + footer sombre + grand mot-marque au scroll */}
      <div className="relative bg-[hsl(250_14%_7%)]">
        <section className="relative z-10 overflow-hidden rounded-b-[2.25rem] bg-background px-4 pb-16 pt-16 sm:rounded-b-[2.75rem] sm:px-6 sm:pb-20 sm:pt-20">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_50%_0%,hsl(var(--brand)/0.14)_0%,transparent_55%)]"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,hsl(var(--foreground)/0.03)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--foreground)/0.03)_1px,transparent_1px)] bg-[size:32px_32px] opacity-70"
          />
          <div className="relative mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl sm:leading-tight">
              {t("landing.cta_title")}
            </h2>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Button
                asChild
                size="lg"
                className="h-12 rounded-xl bg-foreground px-7 text-background hover:bg-foreground/90"
              >
                <Link to="/login?mode=register">{t("landing.cta_button")}</Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-12 rounded-xl border-border bg-card px-7"
              >
                <Link to="/login">{t("landing.login")}</Link>
              </Button>
            </div>
          </div>
        </section>

        <footer className="relative z-0 overflow-hidden text-[hsl(270_12%_92%)]">
          <div className="mx-auto grid max-w-6xl gap-12 px-4 pb-10 pt-14 sm:px-6 lg:grid-cols-12 lg:gap-10 lg:pt-16">
            <div className="lg:col-span-4">
              <div className="flex items-center">
                <BrandLogo on="dark" className="h-8" />
              </div>
              <p className="mt-4 max-w-sm text-sm leading-relaxed text-[hsl(270_8%_62%)]">
                {t("landing.footer_tagline")}
              </p>
              <p className="mt-5 inline-flex items-center gap-2 text-xs font-medium text-[hsl(160_40%_55%)]">
                <span className="size-1.5 rounded-full bg-[hsl(160_50%_45%)]" />
                {t("landing.footer_online")}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-8 sm:grid-cols-4 lg:col-span-8 lg:gap-6">
              {(
                [
                  {
                    titleKey: "landing.footer_product",
                    links: [
                      { labelKey: "landing.footer_community", href: "#communauté" },
                      { labelKey: "landing.footer_marketplace", href: "#marketplace" },
                      { labelKey: "landing.footer_hub", href: "#hub" },
                      { labelKey: "landing.footer_world", href: "#monde" },
                    ],
                  },
                  {
                    titleKey: "landing.footer_space",
                    links: [
                      { labelKey: "landing.footer_login", to: "/login" },
                      { labelKey: "landing.footer_register", to: "/login?mode=register" },
                      { labelKey: "landing.footer_home", href: "#produit" },
                    ],
                  },
                  {
                    titleKey: "landing.footer_audience",
                    links: [
                      { labelKey: "landing.footer_devs", href: "#marketplace" },
                      { labelKey: "landing.footer_recruiters", href: "#marketplace" },
                      { labelKey: "landing.footer_maintainers", href: "#hub" },
                    ],
                  },
                  {
                    titleKey: "landing.footer_legal",
                    links: [
                      { labelKey: "landing.footer_privacy", href: "#produit" },
                      { labelKey: "landing.footer_terms", href: "#produit" },
                    ],
                  },
                ] as const
              ).map((col) => (
                <div key={col.titleKey}>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[hsl(270_8%_48%)]">
                    {t(col.titleKey)}
                  </p>
                  <ul className="mt-4 space-y-2.5 text-sm text-[hsl(270_10%_72%)]">
                    {col.links.map((link) => (
                      <li key={link.labelKey}>
                        {"to" in link && link.to ? (
                          <Link
                            to={link.to}
                            className="transition-colors hover:text-[hsl(270_12%_96%)]"
                          >
                            {t(link.labelKey)}
                          </Link>
                        ) : (
                          <a
                            href={"href" in link ? link.href : "#"}
                            className="transition-colors hover:text-[hsl(270_12%_96%)]"
                          >
                            {t(link.labelKey)}
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          <div className="mx-auto flex max-w-6xl flex-col gap-3 border-t border-white/10 px-4 py-6 text-xs text-[hsl(270_8%_48%)] sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <p>{t("landing.footer_rights", { year: new Date().getFullYear() })}</p>
            <a
              href="#top"
              className="inline-flex items-center gap-1.5 transition-colors hover:text-[hsl(270_12%_92%)]"
            >
              {t("landing.footer_top")}
              <ArrowUp className="size-3.5" aria-hidden />
            </a>
          </div>

          {/* Grand mot-marque : sticky bottom → révélation au scroll final */}
          <div
            aria-hidden
            className="pointer-events-none sticky bottom-0 z-0 flex justify-center overflow-hidden pt-6"
          >
            <p className="select-none whitespace-nowrap text-center text-[18vw] font-bold leading-[0.78] tracking-tighter text-white/[0.07] sm:text-[16vw] md:text-[14vw]">
              DevStreet
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

/** Empilement sticky type Monerails : chaque carte reste, la suivante glisse par-dessus. */
function FeatureStack() {
  const { t } = useTranslation();
  const cardRefs = useRef<(HTMLElement | null)[]>([]);
  const [scales, setScales] = useState(() => FEATURES.map(() => 1));

  useEffect(() => {
    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;
    if (reduceMotion) return;

    let frame = 0;

    const update = () => {
      frame = 0;
      const next = FEATURES.map((_, i) => {
        const el = cardRefs.current[i];
        const following = cardRefs.current[i + 1];
        if (!el || !following) return 1;

        const a = el.getBoundingClientRect();
        const b = following.getBoundingClientRect();
        // Progression 0→1 quand la carte suivante recouvre celle-ci
        const covered = Math.min(
          1,
          Math.max(0, (a.top + a.height * 0.15 - b.top) / (a.height * 0.55))
        );
        return 1 - covered * 0.06;
      });
      setScales((prev) =>
        prev.every((v, i) => Math.abs(v - next[i]) < 0.002) ? prev : next
      );
    };

    const onScroll = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(update);
    };

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <section className="relative px-4 pb-8 sm:px-6 sm:pb-12 lg:pb-24">
      <div className="mx-auto max-w-6xl">
        {FEATURES.map((feature, index) => {
          const nextId = FEATURES[index + 1]?.id;
          const isLast = index === FEATURES.length - 1;

          return (
            <div
              key={feature.id}
              ref={(node) => {
                cardRefs.current[index] = node;
              }}
              className={`relative lg:sticky ${isLast ? "mb-0" : "mb-6 lg:mb-10"}`}
              style={{
                top: `calc(5.25rem + ${index * 0.85}rem)`,
                zIndex: index + 1,
              }}
            >
              <article
                id={feature.id}
                className="scroll-mt-28 grid overflow-hidden rounded-[2rem] border border-border/70 bg-card shadow-[0_12px_40px_hsl(var(--foreground)/0.08)] will-change-transform lg:grid-cols-2"
                style={{
                  transform: `scale(${scales[index]})`,
                  transformOrigin: "center top",
                  transition: "transform 80ms linear",
                }}
              >
                <div
                  className={`flex flex-col justify-center p-8 sm:p-10 lg:p-12 ${
                    feature.reverse ? "order-2 lg:order-1" : ""
                  }`}
                >
                  <p className="inline-flex w-fit rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
                    {t(feature.labelKey)}
                  </p>
                  <h3 className="mt-4 text-2xl font-bold tracking-tight sm:text-3xl sm:leading-tight">
                    {t(feature.titleKey)}
                  </h3>
                  <p className="mt-4 text-sm leading-relaxed text-muted-foreground sm:text-base">
                    {t(feature.bodyKey)}
                  </p>
                  <Button
                    asChild
                    className="mt-8 h-11 w-fit rounded-xl bg-foreground px-5 text-background hover:bg-foreground/90"
                  >
                    <Link to={feature.href}>
                      {t(feature.ctaKey)}
                      <ArrowRight className="ml-1.5 size-4" aria-hidden />
                    </Link>
                  </Button>
                </div>

                <div
                  className={`relative min-h-[280px] overflow-hidden sm:min-h-[340px] ${feature.panelClass} ${
                    feature.reverse ? "order-1 lg:order-2" : ""
                  }`}
                >
                  <div
                    aria-hidden
                    className={`absolute inset-0 bg-[size:28px_28px] ${feature.gridClass}`}
                  />
                  {feature.visual}
                  <div className="absolute bottom-6 left-1/2 flex size-14 -translate-x-1/2 items-center justify-center rounded-2xl bg-foreground text-background shadow-lg">
                    {feature.icon}
                  </div>
                  {nextId ? (
                    <a
                      href={`#${nextId}`}
                      aria-label={t(FEATURES[index + 1].labelKey)}
                      className="absolute right-4 top-4 z-20 flex size-10 items-center justify-center rounded-full bg-foreground text-background shadow-md transition-transform hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <ArrowDown className="size-4" aria-hidden />
                    </a>
                  ) : null}
                </div>
              </article>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function OrbitPill({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`absolute z-10 inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/95 px-3.5 py-2 text-xs font-medium shadow-[0_8px_24px_hsl(var(--foreground)/0.08)] backdrop-blur-sm ${className ?? ""}`}
    >
      {children}
    </div>
  );
}
