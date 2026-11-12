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

export default function GeneralMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const { canViewElitests, canViewElitesties, canViewDragons, canViewFusions, canViewGados } = usePermissions();

  const generalMenu = [
    {
      items: [
        {
          title: "Elitests",
          url: "elitests",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewElitests,
        },
        {
          title: "Elitesties",
          url: "elitesties",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewElitesties,
        },
        {
          title: "Dragons",
          url: "dragons",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewDragons,
        },
        {
          title: "Fusions",
          url: "fusions",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewFusions,
        },
        {
          title: "Gados",
          url: "gados",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewGados,
        },
      ] as {
        title: string;
        url: string;
        isActive: boolean;
        icon: typeof Icons.Home;
        permission: boolean;
      }[],
    },
  ];

  const filteredGeneralMenu = generalMenu.map((group) => ({
    ...group,
    items: group.items
      .filter((item) => item.permission)
      .map((item) => ({
        ...item,
        isActive: location.pathname === `/${item.url}`,
      })),
  }));

  const hasItems = filteredGeneralMenu.some((group) => group.items.length > 0);
  if (!hasItems) {
    return null;
  }

  return (
    <SidebarMenu>
      <Collapsible defaultOpen className="group/collapsible">
        <SidebarGroup>
          <SidebarGroupLabel asChild>
            <CollapsibleTrigger>
              <Icons.Home className="mr-2 h-4 w-4" />
              {t("sidebar.general")}
              <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
            </CollapsibleTrigger>
          </SidebarGroupLabel>
          <CollapsibleContent>
            <SidebarContent className="ml-2">
              <SidebarMenu>
                {filteredGeneralMenu.map((group, groupIndex) =>
                  group.items.map((item) => (
                    <SidebarMenuItem key={`${groupIndex}-${item.title}`}>
                      <SidebarMenuButton asChild isActive={item.isActive}>
                        <button
                          onClick={() => {
                            navigate(item.url);
                            if (isMobile) setOpenMobile(false);
                          }}
                          className="flex items-center gap-2"
                        >
                          {React.createElement(item.icon)}
                          <span>{item.title} </span>
                        </button>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  )),
                )}
              </SidebarMenu>
            </SidebarContent>
          </CollapsibleContent>
        </SidebarGroup>
      </Collapsible>
    </SidebarMenu>
  );
}
