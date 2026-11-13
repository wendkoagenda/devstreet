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
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  ChevronDown,
  Layers,
  Mail,
  MessageSquare,
  Radio,
  Store,
  UserRound,
  Users,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { usePermissions } from "@/hooks/use-permissions";
import { MARKETPLACE_ADMIN_PAGES } from "@/models/marketplace-space/admin-pages";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { useGetActivityBadgesQuery } from "@/models/forum/api";

function formatBadge(count: number | undefined) {
  if (!count || count <= 0) return null;
  return count > 9 ? "9+" : String(count);
}

export default function PlatformMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const permissions = usePermissions();
  const { hasProfil, isRecruiter } = useMySpace();
  const hubActive = location.pathname.startsWith("/hub");
  const { data: badges } = useGetActivityBadgesQuery(undefined, {
    pollingInterval: 30000,
  });

  // Écrans de la marketplace : ceux qui supposent un profil n'apparaissent qu'une fois le profil créé,
  // ceux du recruteur qu'une fois l'entreprise créée
  const marketplaceItems = [
    {
      title: "Tableau de bord",
      url: "/marketplace",
      visible: true,
      exact: true,
    },
    { title: "Mon profil pro", url: "/marketplace/profile", visible: true },
    { title: "Offres pour moi", url: "/marketplace/offers", visible: hasProfil },
    {
      title: "Mes candidatures",
      url: "/marketplace/applications",
      visible: hasProfil,
    },
    { title: "Mes offres", url: "/marketplace/my-offers", visible: isRecruiter },
    { title: "Talents", url: "/marketplace/talents", visible: isRecruiter },
    { title: "Vivier", url: "/marketplace/talents/pool", visible: isRecruiter },
    { title: "Réseau", url: "/marketplace/network", visible: hasProfil },
    {
      title: "Mes disponibilités",
      url: "/marketplace/availability",
      visible: hasProfil,
    },
    { title: "Mon CV", url: "/marketplace/cv", visible: hasProfil },
  ].filter((item) => item.visible);
  // L'administration (listes CRUD) n'apparaît que pour les rôles qui ont au moins une permission de lecture
  const canAdministerMarketplace = MARKETPLACE_ADMIN_PAGES.some(
    (page) => permissions[page.permission]
  );
  const marketplaceActive =
    location.pathname.startsWith("/marketplace") ||
    location.pathname.startsWith("/admin/marketplace");

  // Entrée active : page exacte ou sous-page, sauf si une autre entrée plus précise correspond (ex. /talents/pool)
  const isItemActive = (url: string) => {
    const path = location.pathname;
    if (path === url) return true;
    if (marketplaceItems.find((item) => item.url === url)?.exact) return false;
    if (!path.startsWith(`${url}/`)) return false;
    return !marketplaceItems.some(
      (other) =>
        other.url !== url &&
        other.url.startsWith(`${url}/`) &&
        (path === other.url || path.startsWith(`${other.url}/`))
    );
  };

  const go = (url: string) => {
    navigate(url);
    if (isMobile) setOpenMobile(false);
  };

  const communautesBadge = formatBadge(badges?.communautes);
  const chainesBadge = formatBadge(badges?.chaines);
  const messagesBadge = formatBadge(badges?.messages);

  return (
    <SidebarMenu>
      <SidebarGroup>
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
                      isActive={isItemActive(item.url)}
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
                {canAdministerMarketplace ? (
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      isActive={location.pathname.startsWith(
                        "/admin/marketplace"
                      )}
                      onClick={() => go("/admin/marketplace")}
                    >
                      <span
                        className="size-1.5 rounded-full bg-accent"
                        aria-hidden
                      />
                      <span>Administration</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ) : null}
              </SidebarMenu>
            </SidebarContent>
          </CollapsibleContent>
        </Collapsible>

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
            isActive={
              location.pathname === "/" ||
              (location.pathname.startsWith("/forum/") &&
                !location.pathname.startsWith("/forum/profil") &&
                !location.pathname.startsWith("/forum/communautes") &&
                !location.pathname.startsWith("/forum/chaines"))
            }
            onClick={() => go("/")}
            tooltip="Forum"
          >
            <MessageSquare />
            <span>Forum</span>
          </SidebarMenuButton>
        </SidebarMenuItem>

        <SidebarMenuItem>
          <SidebarMenuButton
            isActive={location.pathname.startsWith("/forum/communautes")}
            onClick={() => go("/forum/communautes")}
            tooltip="Communautés"
          >
            <Users />
            <span>Communautés</span>
          </SidebarMenuButton>
          {communautesBadge ? (
            <SidebarMenuBadge className="bg-destructive text-destructive-foreground">
              {communautesBadge}
            </SidebarMenuBadge>
          ) : null}
        </SidebarMenuItem>

        <SidebarMenuItem>
          <SidebarMenuButton
            isActive={location.pathname.startsWith("/forum/chaines")}
            onClick={() => go("/forum/chaines")}
            tooltip="Chaînes"
          >
            <Radio />
            <span>Chaînes</span>
          </SidebarMenuButton>
          {chainesBadge ? (
            <SidebarMenuBadge className="bg-destructive text-destructive-foreground">
              {chainesBadge}
            </SidebarMenuBadge>
          ) : null}
        </SidebarMenuItem>

        <SidebarMenuItem>
          <SidebarMenuButton
            isActive={location.pathname.startsWith("/messages")}
            onClick={() => go("/messages")}
            tooltip="Messages"
          >
            <Mail />
            <span>Messages</span>
          </SidebarMenuButton>
          {messagesBadge ? (
            <SidebarMenuBadge className="bg-destructive text-destructive-foreground">
              {messagesBadge}
            </SidebarMenuBadge>
          ) : null}
        </SidebarMenuItem>

        <SidebarMenuItem>
          <SidebarMenuButton
            isActive={location.pathname.startsWith("/forum/profil")}
            onClick={() => go("/forum/profil/me")}
          >
            <UserRound />
            <span>Mon compte</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarGroup>
    </SidebarMenu>
  );
}
