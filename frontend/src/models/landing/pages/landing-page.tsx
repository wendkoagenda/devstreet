import {
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { Button } from "@/components/ui/button";
import {
  ArrowDown,
  ArrowRight,
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
import { AfricaCommunitySection } from "../components/africa-community-section";
import { CountUp } from "../components/count-up";
import { LandingFooter } from "../components/landing-footer";
import { LandingHeader } from "../components/landing-header";
import { LandingSelinaHost } from "../components/landing-selina-host";
import { ProfilesMarquee } from "../components/profiles-marquee";
import { Reveal } from "../components/reveal";
import { ToolOrbits } from "../components/tool-orbits";

const STATS = [
  { value: 54, labelKey: "landing.stat_countries" },
  { value: 3, labelKey: "landing.stat_spaces" },
  { value: 1, labelKey: "landing.stat_account" },
  { value: "CV", labelKey: "landing.stat_cv" },
  { value: "Match", labelKey: "landing.stat_connections" },
] as const;

const HERO_ENTER =
  "animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-both motion-reduce:animate-none";

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
        <OrbitPill className="right-[10%] top-[28%]" delay={1.5}>
          <Users className="size-3.5 text-brand" />
          core-maintainers
        </OrbitPill>
        <OrbitPill className="left-[18%] bottom-[28%]" delay={3}>
          <MessageSquare className="size-3.5 text-brand" />
          Aide confirmée
        </OrbitPill>
        <OrbitPill className="right-[14%] bottom-[18%]" delay={4.5}>
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
        <OrbitPill className="right-[8%] top-[32%]" delay={1.5}>React · 4 ans</OrbitPill>
        <OrbitPill className="left-[16%] bottom-[30%]" delay={3}>
          <span className="font-semibold text-brand">94 %</span>
          match
        </OrbitPill>
        <OrbitPill className="right-[12%] bottom-[16%]" delay={4.5}>
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
        <OrbitPill className="right-[10%] top-[30%]" delay={1.5}>
          <GitPullRequest className="size-3.5 text-success" />
          PR validée
        </OrbitPill>
        <OrbitPill className="left-[18%] bottom-[28%]" delay={3}>
          <Sparkles className="size-3.5 text-brand" />
          Atelier IA
        </OrbitPill>
        <OrbitPill className="right-[14%] bottom-[16%]" delay={4.5}>
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
      <LandingHeader showProductNav showScrollProgress />

      <main>
        <div className="relative flex min-h-[calc(100svh-4.25rem)] flex-col overflow-hidden">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 bottom-0 h-[60%] bg-[radial-gradient(ellipse_at_50%_100%,hsl(var(--brand)/0.14)_0%,transparent_70%)]"
          />

          <section className="relative flex flex-1 items-center pb-4 pt-8 sm:pt-12">
            <ToolOrbits />

            <div className="relative z-10 mx-auto max-w-4xl px-4 text-center sm:px-6">
              <h1 className="text-[2.25rem] font-bold leading-[1.06] tracking-tight sm:text-5xl sm:leading-[1.05] lg:text-[3.5rem]">
                <span className={`block ${HERO_ENTER}`}>
                  {t("landing.hero_line1")}
                </span>
                <span className={`block ${HERO_ENTER}`} style={{ animationDelay: "100ms" }}>
                  {t("landing.hero_line2")}
                </span>
                <span
                  className={`block bg-gradient-to-r from-brand via-brand to-success bg-clip-text text-transparent ${HERO_ENTER}`}
                  style={{ animationDelay: "200ms" }}
                >
                  {t("landing.hero_line3")}
                </span>
              </h1>

              <p
                className={`mx-auto mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-[1.0625rem] ${HERO_ENTER}`}
                style={{ animationDelay: "320ms" }}
              >
                {t("landing.hero_sub")}
              </p>

              <div
                className={`mt-7 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 ${HERO_ENTER}`}
                style={{ animationDelay: "440ms" }}
              >
                <Button
                  asChild
                  size="lg"
                  className="group h-12 rounded-xl bg-foreground px-7 text-background hover:bg-foreground/90"
                >
                  <Link to="/login?mode=register">
                    {t("landing.create_account")}
                    <ArrowRight
                      className="ml-1.5 size-4 transition-transform group-hover:translate-x-1"
                      aria-hidden
                    />
                  </Link>
                </Button>
                <Link
                  to="/login"
                  className="text-[0.9375rem] font-medium text-foreground underline-offset-4 transition-colors hover:underline"
                >
                  {t("landing.have_account")}
                </Link>
              </div>

              <div
                className={`mt-10 ${HERO_ENTER}`}
                style={{ animationDelay: "560ms" }}
              >
                <LandingSelinaHost />
              </div>
            </div>
          </section>

          <div className={`relative z-10 pb-6 ${HERO_ENTER}`} style={{ animationDelay: "660ms" }}>
            <ProfilesMarquee />
          </div>
        </div>

        <section className="px-4 pb-12 pt-10 sm:px-6 sm:pb-16 sm:pt-14">
          <Reveal className="mx-auto grid max-w-5xl grid-cols-2 gap-y-10 sm:grid-cols-5 sm:gap-0">
            {STATS.map((stat, i) => (
              <div
                key={stat.labelKey}
                className={`flex flex-col items-center px-3 sm:px-5 ${
                  i > 0 ? "sm:border-l sm:border-border" : ""
                }`}
              >
                <span className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                  {typeof stat.value === "number" ? <CountUp value={stat.value} /> : stat.value}
                </span>
                <span className="mt-2 text-sm text-muted-foreground sm:text-base">
                  {t(stat.labelKey)}
                </span>
              </div>
            ))}
          </Reveal>
        </section>

        <section
          id="produit"
          className="scroll-mt-24 pb-6 pt-4 sm:pb-10 sm:pt-8"
        >
          <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 sm:px-6 lg:flex-row lg:items-end lg:justify-between lg:gap-16">
            <Reveal from="left" className="flex max-w-2xl gap-3">
              <span
                aria-hidden
                className="mt-1.5 h-8 w-1 shrink-0 rounded-full bg-gradient-to-b from-brand to-success"
              />
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl sm:leading-tight">
                {t("landing.product_title")}
              </h2>
            </Reveal>
            <Reveal from="right" delay={120}>
              <p className="max-w-md text-sm leading-relaxed text-muted-foreground lg:pb-1 lg:text-right">
                {t("landing.product_sub")}
              </p>
            </Reveal>
          </div>
        </section>

        <FeatureStack />

        <AfricaCommunitySection />
      </main>

      {/* CTA clair (coins bas arrondis) au-dessus du footer sombre */}
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
          <Reveal className="relative mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl sm:leading-tight">
              {t("landing.cta_title")}
            </h2>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Button
                asChild
                size="lg"
                className="group h-12 rounded-xl bg-foreground px-7 text-background hover:bg-foreground/90"
              >
                <Link to="/login?mode=register">
                  {t("landing.cta_button")}
                  <ArrowRight
                    className="ml-1.5 size-4 transition-transform group-hover:translate-x-1"
                    aria-hidden
                  />
                </Link>
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
          </Reveal>
        </section>

        <LandingFooter />
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
              <Reveal from="zoom">
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
                      className="group mt-8 h-11 w-fit rounded-xl bg-foreground px-5 text-background hover:bg-foreground/90"
                    >
                      <Link to={feature.href}>
                        {t(feature.ctaKey)}
                        <ArrowRight
                          className="ml-1.5 size-4 transition-transform group-hover:translate-x-1"
                          aria-hidden
                        />
                      </Link>
                    </Button>
                  </div>

                  <div
                    className={`group/panel relative min-h-[280px] overflow-hidden sm:min-h-[340px] ${feature.panelClass} ${
                      feature.reverse ? "order-1 lg:order-2" : ""
                    }`}
                  >
                    <div
                      aria-hidden
                      className={`absolute inset-0 bg-[size:28px_28px] ${feature.gridClass}`}
                    />
                    {feature.visual}
                    <div className="absolute bottom-6 left-1/2 flex size-14 -translate-x-1/2 items-center justify-center rounded-2xl bg-foreground text-background shadow-lg transition-transform duration-300 group-hover/panel:-translate-y-1 group-hover/panel:rotate-3">
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
              </Reveal>
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
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <div
      style={{ animationDelay: `-${delay}s` }}
      className={`absolute z-10 inline-flex animate-float items-center gap-2 rounded-full border border-border/60 bg-card/95 px-3.5 py-2 text-xs font-medium shadow-[0_8px_24px_hsl(var(--foreground)/0.08)] backdrop-blur-sm motion-reduce:animate-none ${className ?? ""}`}
    >
      {children}
    </div>
  );
}