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
import { MARKETPLACE_ADMIN_PAGES } from "@/models/marketplace-space/admin-pages";

export default function PlatformMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const permissions = usePermissions();
  const hubActive = location.pathname.startsWith("/hub");

  // Écrans de la marketplace pour tout utilisateur connecté (les nouveaux écrans s'ajoutent ici)
  const marketplaceItems = [
    { title: "Mon profil pro", url: "/marketplace/profile" },
  ];
  // L'administration (listes CRUD) n'apparaît que pour les rôles qui ont au moins une permission de lecture
  const canAdministerMarketplace = MARKETPLACE_ADMIN_PAGES.some(
    (page) => permissions[page.permission]
  );
  const marketplaceActive =
    location.pathname.startsWith("/marketplace") ||
    location.pathname.startsWith("/admin/marketplace");

  const go = (url: string) => {
    navigate(url);
    if (isMobile) setOpenMobile(false);
  };

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
            <span>Mon compte</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarGroup>
    </SidebarMenu>
  );
}
