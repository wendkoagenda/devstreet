import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  ChevronDown,
  Layers,
  MessageSquare,
  Store,
  UserRound,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { usePermissions } from "@/hooks/use-permissions";

export default function PlatformMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const hubActive = location.pathname.startsWith("/hub");
  const {
    canViewCompanies,
    canViewSkills,
    canViewProfils,
    canViewOffers,
    canViewCandidatures,
    canViewProfilSkills,
    canViewExperiences,
    canViewPrestations,
    canViewProfilHistories,
    canViewAvailabilities,
    canViewReviews,
    canViewSwipes,
    canViewConnections,
  } = usePermissions();

  // Sous-menus de la Marketplace, affichés selon les permissions de lecture
  const marketplaceItems = [
    { title: "Entreprises", url: "/companies", permission: canViewCompanies },
    { title: "Compétences", url: "/skills", permission: canViewSkills },
    { title: "Profils", url: "/profils", permission: canViewProfils },
    { title: "Offres", url: "/offers", permission: canViewOffers },
    {
      title: "Candidatures",
      url: "/candidatures",
      permission: canViewCandidatures,
    },
    {
      title: "Compétences des profils",
      url: "/profil-skills",
      permission: canViewProfilSkills,
    },
    {
      title: "Expériences",
      url: "/experiences",
      permission: canViewExperiences,
    },
    {
      title: "Prestations",
      url: "/prestations",
      permission: canViewPrestations,
    },
    {
      title: "Historique des profils",
      url: "/profil-histories",
      permission: canViewProfilHistories,
    },
    {
      title: "Disponibilités",
      url: "/availabilities",
      permission: canViewAvailabilities,
    },
    { title: "Avis", url: "/reviews", permission: canViewReviews },
    { title: "Swipes", url: "/swipes", permission: canViewSwipes },
    {
      title: "Connexions",
      url: "/connections",
      permission: canViewConnections,
    },
  ].filter((item) => item.permission);
  const marketplaceActive = marketplaceItems.some(
    (item) => location.pathname === item.url
  );

  const go = (url: string) => {
    navigate(url);
    if (isMobile) setOpenMobile(false);
  };

  return (
    <SidebarMenu>
      <SidebarGroup>
        {marketplaceItems.length > 0 ? (
          <Collapsible
            defaultOpen={marketplaceActive}
            className="group/collapsible"
          >
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center gap-2">
                <Store className="mr-0 h-4 w-4" />
                Marketplace
                <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarContent className="ml-2 border-l border-sidebar-border pl-2">
                <SidebarMenu>
                  {marketplaceItems.map((item) => (
                    <SidebarMenuItem key={item.url}>
                      <SidebarMenuButton
                        isActive={location.pathname === item.url}
                        onClick={() => go(item.url)}
                      >
                        <span
                          className="size-1.5 rounded-full bg-accent"
                          aria-hidden
                        />
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarContent>
            </CollapsibleContent>
          </Collapsible>
        ) : (
          <SidebarMenuItem>
            <SidebarMenuButton
              disabled
              tooltip="Marketplace — aucun accès"
              className="opacity-60"
            >
              <Store />
              <span>Marketplace</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        )}

        <Collapsible defaultOpen={hubActive} className="group/collapsible">
          <SidebarGroupLabel asChild>
            <CollapsibleTrigger className="flex w-full items-center gap-2">
              <Layers className="mr-0 h-4 w-4" />
              DevStreet Hub
              <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
            </CollapsibleTrigger>
          </SidebarGroupLabel>
          <CollapsibleContent>
            <SidebarContent className="ml-2 border-l border-sidebar-border pl-2">
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    isActive={location.pathname.startsWith("/hub/projects")}
                    onClick={() => go("/hub/projects")}
                  >
                    <span className="size-1.5 rounded-full bg-accent" aria-hidden />
                    <span>Explorer les projets</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarContent>
          </CollapsibleContent>
        </Collapsible>

        <SidebarMenuItem>
          <SidebarMenuButton
            disabled
            tooltip="Forum — bientôt disponible"
            className="opacity-60"
          >
            <MessageSquare />
            <span>Forum</span>
            <span className="ml-auto text-[10px] text-muted-foreground">
              bientôt
            </span>
          </SidebarMenuButton>
        </SidebarMenuItem>

        <SidebarMenuItem>
          <SidebarMenuButton
            isActive={location.pathname === "/my-account"}
            onClick={() => go("/my-account")}
          >
            <UserRound />
            <span>Mon profil</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarGroup>
    </SidebarMenu>
  );
}
