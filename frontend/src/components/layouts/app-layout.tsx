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
  };

  // Générer les breadcrumbs
  const breadcrumbs = generateBreadcrumbs(location.pathname, breadcrumbTitles);
  return (
    <SidebarProvider>
      {/* Sidebar */}
      <AppSidebar />

      {/* Contenu principal */}
      <div className="flex-1 overflow-auto">
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
            <div className="flex items-center gap-2 px-4">
              <SidebarTrigger className="-ml-1" />
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
          <div className="flex flex-col gap-4 p-6">
            <Outlet />
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
