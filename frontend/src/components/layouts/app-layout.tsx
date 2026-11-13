import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { generateBreadcrumbs } from "@/helpers/displayers/generate-breadcrumbs";
import { t } from "i18next";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import React from "react";
import { AppSidebar } from "../sidebar/app-sidebar";

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  // Mapping entre URLs et titres compréhensibles
  const breadcrumbTitles: Record<string, string> = {
    "/": t("breadcrumb_titles.home"),
    "/users": t("breadcrumb_titles.users_list"),
    "/roles": t("breadcrumb_titles.roles_list"),
    "/hub": t("breadcrumb_titles.hub"),
    "/hub/projects": t("breadcrumb_titles.hub_projects"),
    "/hub/projects/new": t("breadcrumb_titles.hub_project_new"),
    "/hub/projects/*": t("breadcrumb_titles.hub_project_detail"),
    "/marketplace": t("breadcrumb_titles.marketplace"),
    "/marketplace/profile": t("breadcrumb_titles.marketplace_profile"),
    "/marketplace/offers": t("breadcrumb_titles.marketplace_offers_list"),
    "/marketplace/offers/*": t("breadcrumb_titles.marketplace_offer"),
    "/marketplace/offers/*/apply": t("breadcrumb_titles.marketplace_apply"),
    "/marketplace/applications": t("breadcrumb_titles.marketplace_applications"),
    "/marketplace/my-offers": t("breadcrumb_titles.marketplace_my_offers"),
    "/marketplace/my-offers/new": t("breadcrumb_titles.marketplace_offer_new"),
    "/marketplace/my-offers/*": t("breadcrumb_titles.marketplace_offer_manage"),
    "/marketplace/my-offers/*/edit": t("breadcrumb_titles.marketplace_offer_edit"),
    "/marketplace/talents": t("breadcrumb_titles.marketplace_talents"),
    "/marketplace/talents/pool": t("breadcrumb_titles.marketplace_pool"),
    "/marketplace/network": t("breadcrumb_titles.marketplace_network"),
    "/marketplace/profiles": t("breadcrumb_titles.marketplace_profiles"),
    "/marketplace/profiles/*": t("breadcrumb_titles.marketplace_profile_view"),
    "/marketplace/availability": t("breadcrumb_titles.marketplace_availability"),
    "/marketplace/cv": t("breadcrumb_titles.marketplace_cv"),
    "/admin": t("breadcrumb_titles.admin"),
    "/admin/marketplace": t("breadcrumb_titles.marketplace_admin"),
    "/admin/marketplace/companies": t("breadcrumb_titles.marketplace_companies"),
    "/admin/marketplace/skills": t("breadcrumb_titles.marketplace_skills"),
    "/admin/marketplace/profils": t("breadcrumb_titles.marketplace_profils"),
    "/admin/marketplace/offers": t("breadcrumb_titles.marketplace_offers"),
    "/admin/marketplace/candidatures": t("breadcrumb_titles.marketplace_candidatures"),
    "/admin/marketplace/profil-skills": t("breadcrumb_titles.marketplace_profil_skills"),
    "/admin/marketplace/experiences": t("breadcrumb_titles.marketplace_experiences"),
    "/admin/marketplace/prestations": t("breadcrumb_titles.marketplace_prestations"),
    "/admin/marketplace/profil-histories": t("breadcrumb_titles.marketplace_profil_histories"),
    "/admin/marketplace/availabilities": t("breadcrumb_titles.marketplace_availabilities"),
    "/admin/marketplace/reviews": t("breadcrumb_titles.marketplace_reviews"),
    "/admin/marketplace/swipes": t("breadcrumb_titles.marketplace_swipes"),
    "/admin/marketplace/connections": t("breadcrumb_titles.marketplace_connections"),
  };

  // Générer les breadcrumbs
  const breadcrumbs = generateBreadcrumbs(location.pathname, breadcrumbTitles);
  return (
    <SidebarProvider
      defaultOpen
      style={{ "--sidebar-width": "17rem" } as React.CSSProperties}
    >
      <AppSidebar />

      <div className="min-w-0 flex-1 overflow-auto">
        <SidebarInset className="bg-background">
          <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center gap-2 border-b border-border/70 bg-background/85 backdrop-blur-md transition-[width,height] ease-linear supports-[backdrop-filter]:bg-background/70">
            <div className="flex items-center gap-2 px-4">
              <SidebarTrigger className="-ml-1 rounded-xl" />
              <Separator orientation="vertical" className="mr-2 h-4" />
              <Breadcrumb>
                <BreadcrumbList>
                  {/* Lien vers la page d'accueil */}
                  <BreadcrumbItem className="hidden md:block">
                    <BreadcrumbLink>
                      <button
                        onClick={() => {
                          navigate("/");
                        }}
                      >
                        {t("sidebar.title")}
                      </button>
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="hidden md:block" />
                  {/* Breadcrumbs dynamiques */}
                  {breadcrumbs.map((breadcrumb, index) => (
                    <React.Fragment key={breadcrumb.url}>
                      <BreadcrumbItem
                        className={index === 0 ? "hidden md:block" : ""}
                      >
                        {!breadcrumb.isLast ? (
                          <>
                            <BreadcrumbLink className="hidden md:block">
                              <button
                                onClick={() => {
                                  // Gestion spéciale pour la route myyear
                                  if (breadcrumb.url === "/myyear") {
                                    const dcnf_uuid = localStorage.getItem(
                                      "dasdgcnf_uuid_sdfjwe"
                                    );
                                    const dcnf_id = localStorage.getItem(
                                      "sgasdksjdcnf_id_sdfjwe"
                                    );
                                    if (dcnf_uuid && dcnf_id) {
                                      navigate(
                                        `/myyear/${dcnf_uuid}/${dcnf_id}`
                                      );
                                    } else {
                                      navigate("/myyear");
                                    }
                                  } else {
                                    navigate(breadcrumb.url);
                                  }
                                }}
                              >
                                {breadcrumb.title}
                              </button>
                            </BreadcrumbLink>
                          </>
                        ) : (
                          <BreadcrumbPage>{breadcrumb.title}</BreadcrumbPage>
                        )}
                      </BreadcrumbItem>
                      {!breadcrumb.isLast ? (
                        <BreadcrumbSeparator className="hidden md:block" />
                      ) : (
                        ""
                      )}
                    </React.Fragment>
                  ))}
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <div className="flex flex-col gap-4 p-4 sm:p-6 lg:p-8">
            <Outlet />
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
