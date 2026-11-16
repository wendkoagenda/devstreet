import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useLocation } from "react-router-dom";
import { LandingFooter } from "../components/landing-footer";
import { LandingHeader } from "../components/landing-header";
import { getLegalDocument, type LegalDocument } from "../data/legal-documents";

const SLUGS = new Set<LegalDocument["slug"]>(["confidentialite", "conditions"]);

export default function LegalPage() {
  const { pathname } = useLocation();
  const slug = pathname.replace(/^\//, "") as LegalDocument["slug"];
  const { i18n, t } = useTranslation();
  const legal = SLUGS.has(slug) ? getLegalDocument(slug, i18n.language) : null;

  useEffect(() => {
    if (!legal) return;
    window.scrollTo(0, 0);
    const previous = window.document.title;
    window.document.title = `${legal.title} · DevStreet`;
    return () => {
      window.document.title = previous;
    };
  }, [legal]);

  if (!legal) {
    return <Navigate to="/welcome" replace />;
  }

  const other =
    slug === "confidentialite"
      ? { to: "/conditions", label: t("landing.footer_terms") }
      : { to: "/confidentialite", label: t("landing.footer_privacy") };

  return (
    <div id="top" className="min-h-svh bg-background text-foreground">
      <LandingHeader />

      <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
        <p className="text-sm text-muted-foreground">
          <Link to="/welcome" className="transition-colors hover:text-foreground">
            {t("landing.footer_home")}
          </Link>
          <span className="mx-2 text-border">/</span>
          <span>{legal.title}</span>
        </p>

        <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
          {legal.title}
        </h1>
        <p className="mt-3 text-sm text-muted-foreground">
          {t("landing.legal_updated", { date: legal.updatedAt })}
        </p>

        <p className="mt-8 text-base leading-relaxed text-muted-foreground">
          {legal.intro}
        </p>
        <p className="mt-4 rounded-2xl border border-border/70 bg-muted/40 p-4 text-sm leading-relaxed text-muted-foreground">
          {legal.disclaimer}
        </p>

        <nav
          aria-label={t("landing.legal_toc")}
          className="mt-10 rounded-2xl border border-border/70 bg-card p-5"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            {t("landing.legal_toc")}
          </p>
          <ol className="mt-3 space-y-2 text-sm">
            {legal.sections.map((section) => (
              <li key={section.id}>
                <a
                  href={`#${section.id}`}
                  className="text-foreground/80 transition-colors hover:text-foreground"
                >
                  {section.title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        <div className="mt-12 space-y-10">
          {legal.sections.map((section) => (
            <section key={section.id} id={section.id} className="scroll-mt-28">
              <h2 className="text-xl font-semibold tracking-tight">{section.title}</h2>
              <div className="mt-3 space-y-3 text-sm leading-relaxed text-muted-foreground sm:text-[0.9375rem]">
                {section.paragraphs.map((paragraph, index) => (
                  <p key={`${section.id}-p-${index}`}>{paragraph}</p>
                ))}
                {section.bullets ? (
                  <ul className="list-disc space-y-2 pl-5">
                    {section.bullets.map((bullet, index) => (
                      <li key={`${section.id}-b-${index}`}>{bullet}</li>
                    ))}
                  </ul>
                ) : null}
              </div>
            </section>
          ))}
        </div>

        <p className="mt-14 text-sm text-muted-foreground">
          {t("landing.legal_also_see")}{" "}
          <Link
            to={other.to}
            className="font-medium text-foreground underline-offset-4 hover:underline"
          >
            {other.label}
          </Link>
          .
        </p>
      </main>

      <LandingFooter />
    </div>
  );
}
