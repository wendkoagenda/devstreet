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

export default function PlatformMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const hubActive = location.pathname.startsWith("/hub");

  const go = (url: string) => {
    navigate(url);
    if (isMobile) setOpenMobile(false);
  };

  return (
    <SidebarMenu>
      <SidebarGroup>
        <SidebarMenuItem>
          <SidebarMenuButton
            disabled
            tooltip="Marketplace — bientôt disponible"
            className="opacity-60"
          >
            <Store />
            <span>Marketplace</span>
            <span className="ml-auto font-mono text-[10px] text-muted-foreground">
              bientôt
            </span>
          </SidebarMenuButton>
        </SidebarMenuItem>

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
            <span className="ml-auto font-mono text-[10px] text-muted-foreground">
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
