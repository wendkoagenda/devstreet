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
  const { canViewCompanies, canViewSkills, canViewProfils, canViewOffers, canViewCandidatures, canViewProfilSkills, canViewExperiences, canViewPrestations, canViewProfilHistories, canViewAvailabilities, canViewReviews, canViewSwipes, canViewConnections } = usePermissions();

  const generalMenu = [
    {
      items: [
        {
          title: "Companies",
          url: "companies",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewCompanies,
        },
        {
          title: "Skills",
          url: "skills",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewSkills,
        },
        {
          title: "Profils",
          url: "profils",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewProfils,
        },
        {
          title: "Offers",
          url: "offers",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewOffers,
        },
        {
          title: "Candidatures",
          url: "candidatures",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewCandidatures,
        },
        {
          title: "Profil-skills",
          url: "profil-skills",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewProfilSkills,
        },
        {
          title: "Experiences",
          url: "experiences",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewExperiences,
        },
        {
          title: "Prestations",
          url: "prestations",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewPrestations,
        },
        {
          title: "Profil-histories",
          url: "profil-histories",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewProfilHistories,
        },
        {
          title: "Availabilities",
          url: "availabilities",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewAvailabilities,
        },
        {
          title: "Reviews",
          url: "reviews",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewReviews,
        },
        {
          title: "Swipes",
          url: "swipes",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewSwipes,
        },
        {
          title: "Connections",
          url: "connections",
          isActive: false,
          icon: Icons.FileText,
          permission: canViewConnections,
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
