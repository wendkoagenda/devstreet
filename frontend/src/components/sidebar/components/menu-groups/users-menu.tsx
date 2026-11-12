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
import { usePermissions } from "@/hooks/use-permissions";
import { Icons } from "@/lib/constants/icons";
import { t } from "i18next";
import { ChevronDown } from "lucide-react";
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function UsersMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const { canViewUsers, canViewRoles } = usePermissions();

  const menuItems = [
    {
      title: t("sidebar.users"),
      url: "users",
      icon: Icons.User,
      permission: canViewUsers,
    },
    {
      title: t("sidebar.roles"),
      url: "roles",
      icon: Icons.Roles,
      permission: canViewRoles,
    },
  ].filter((item) => item.permission); // Filtrage direct des items sans permission

  // Ne pas afficher le menu s'il n'y a aucun élément
  if (menuItems.length === 0) {
    return null;
  }

  return (
    <SidebarMenu>
      <Collapsible defaultOpen className="group/collapsible">
        <SidebarGroup>
          <SidebarGroupLabel asChild>
            <CollapsibleTrigger>
              <Icons.User className="mr-2 h-4 w-4" />
              {t("sidebar.users")}
              <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
            </CollapsibleTrigger>
          </SidebarGroupLabel>
          <CollapsibleContent>
            <SidebarContent className="ml-2">
              <SidebarMenu>
                {menuItems.map((item) => {
                  const isActive = location.pathname === `/${item.url}`;

                  return (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild isActive={isActive}>
                        <button
                          onClick={() => {
                            navigate(item.url);
                            if (isMobile) setOpenMobile(false);
                          }}
                          className="flex items-center gap-2"
                        >
                          {React.createElement(item.icon)}
                          <span>{item.title}</span>
                        </button>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarContent>
          </CollapsibleContent>
        </SidebarGroup>
      </Collapsible>
    </SidebarMenu>
  );
}
