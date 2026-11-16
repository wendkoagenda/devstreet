import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { BrandLogo } from "@/components/brand/brand-logo";
import { Button } from "@/components/ui/button";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { ScrollProgress } from "./scroll-progress";

export function LandingHeader({
  showProductNav = false,
  showScrollProgress = false,
}: {
  showProductNav?: boolean;
  showScrollProgress?: boolean;
}) {
  const { t } = useTranslation();

  return (
    <header className="sticky top-0 z-40 bg-background/85 backdrop-blur-md">
      {showScrollProgress ? <ScrollProgress /> : null}
      <div className="mx-auto flex h-[4.25rem] max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-10">
          <Link
            to="/welcome"
            className="flex items-center"
            aria-label={t("landing.home_aria")}
          >
            <BrandLogo className="h-8" />
          </Link>

          {showProductNav ? (
            <nav
              aria-label={t("landing.nav_aria")}
              className="hidden items-center gap-8 text-[0.9375rem] font-medium text-muted-foreground md:flex"
            >
              <a href="#produit" className="transition-colors hover:text-foreground">
                {t("landing.nav_product")}
              </a>
              <a href="#communauté" className="transition-colors hover:text-foreground">
                {t("landing.nav_community")}
              </a>
              <a href="#marketplace" className="transition-colors hover:text-foreground">
                {t("landing.nav_marketplace")}
              </a>
              <a href="#hub" className="transition-colors hover:text-foreground">
                {t("landing.nav_hub")}
              </a>
            </nav>
          ) : (
            <nav
              aria-label={t("landing.nav_aria")}
              className="hidden items-center gap-6 text-[0.9375rem] font-medium text-muted-foreground md:flex"
            >
              <Link to="/welcome" className="transition-colors hover:text-foreground">
                {t("landing.footer_home")}
              </Link>
              <Link to="/confidentialite" className="transition-colors hover:text-foreground">
                {t("landing.footer_privacy")}
              </Link>
              <Link to="/conditions" className="transition-colors hover:text-foreground">
                {t("landing.footer_terms")}
              </Link>
            </nav>
          )}
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
  );
}
