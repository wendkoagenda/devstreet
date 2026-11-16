import { ArrowUp } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router-dom";
import { BrandLogo } from "@/components/brand/brand-logo";

type FooterLink =
  | { labelKey: string; to: string }
  | { labelKey: string; href: string };

type FooterColumn = {
  titleKey: string;
  links: FooterLink[];
};

/** Ancres de la landing : depuis une autre page, on préfixe /welcome. */
function landingHash(hash: string, pathname: string) {
  return pathname === "/welcome" ? hash : `/welcome${hash}`;
}

export function LandingFooter() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const year = new Date().getFullYear();

  const columns: FooterColumn[] = [
    {
      titleKey: "landing.footer_product",
      links: [
        { labelKey: "landing.footer_community", href: landingHash("#communauté", pathname) },
        { labelKey: "landing.footer_marketplace", href: landingHash("#marketplace", pathname) },
        { labelKey: "landing.footer_hub", href: landingHash("#hub", pathname) },
        { labelKey: "landing.footer_africa", href: landingHash("#afrique", pathname) },
      ],
    },
    {
      titleKey: "landing.footer_space",
      links: [
        { labelKey: "landing.footer_login", to: "/login" },
        { labelKey: "landing.footer_register", to: "/login?mode=register" },
        { labelKey: "landing.footer_home", to: "/welcome" },
      ],
    },
    {
      titleKey: "landing.footer_audience",
      links: [
        { labelKey: "landing.footer_devs", href: landingHash("#marketplace", pathname) },
        { labelKey: "landing.footer_recruiters", href: landingHash("#marketplace", pathname) },
        { labelKey: "landing.footer_maintainers", href: landingHash("#hub", pathname) },
      ],
    },
    {
      titleKey: "landing.footer_legal",
      links: [
        { labelKey: "landing.footer_privacy", to: "/confidentialite" },
        { labelKey: "landing.footer_terms", to: "/conditions" },
      ],
    },
  ];

  return (
    <footer className="relative z-0 overflow-hidden bg-[hsl(250_14%_7%)] text-[hsl(270_12%_92%)]">
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
          {columns.map((col) => (
            <div key={col.titleKey}>
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[hsl(270_8%_48%)]">
                {t(col.titleKey)}
              </p>
              <ul className="mt-4 space-y-2.5 text-sm text-[hsl(270_10%_72%)]">
                {col.links.map((link) => (
                  <li key={link.labelKey}>
                    {"to" in link ? (
                      <Link
                        to={link.to}
                        className="transition-colors hover:text-[hsl(270_12%_96%)]"
                      >
                        {t(link.labelKey)}
                      </Link>
                    ) : (
                      <a
                        href={link.href}
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
        <p>{t("landing.footer_rights", { year })}</p>
        <a
          href="#top"
          className="inline-flex items-center gap-1.5 transition-colors hover:text-[hsl(270_12%_92%)]"
        >
          {t("landing.footer_top")}
          <ArrowUp className="size-3.5" aria-hidden />
        </a>
      </div>

      <div
        aria-hidden
        className="pointer-events-none sticky bottom-0 z-0 flex justify-center overflow-hidden pt-6"
      >
        <p className="select-none whitespace-nowrap text-center text-[18vw] font-bold leading-[0.78] tracking-tighter text-white/[0.07] sm:text-[16vw] md:text-[14vw]">
          DevStreet
        </p>
      </div>
    </footer>
  );
}
