import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import {
  Bookmark,
  Briefcase,
  CalendarDays,
  ClipboardList,
  FileText,
  FolderKanban,
  Home,
  LayoutDashboard,
  Mail,
  Network,
  Radio,
  Shield,
  Store,
  UserRound,
  Users,
  UsersRound,
  type LucideIcon,
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

type NavItem = {
  title: string;
  url: string;
  icon: LucideIcon;
  exact?: boolean;
  badge?: string | null;
  match?: (path: string) => boolean;
};

const itemClass =
  "h-8 gap-2.5 rounded-lg px-2.5 text-[13px] font-medium text-sidebar-foreground/80 transition-colors duration-150 hover:bg-sidebar-accent/80 hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:font-semibold data-[active=true]:text-sidebar-accent-foreground data-[active=true]:shadow-[inset_0_0_0_1px_hsl(var(--sidebar-border))]";

const sectionLabelClass =
  "mb-0.5 h-auto px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground/80";

function isItemActive(path: string, item: NavItem) {
  if (item.match) return item.match(path);
  if (path === item.url) return true;
  if (item.exact) return false;
  return path.startsWith(`${item.url}/`);
}

function NavList({
  items,
  path,
  onGo,
}: {
  items: NavItem[];
  path: string;
  onGo: (url: string) => void;
}) {
  return (
    <SidebarMenu className="gap-0.5">
      {items.map((item) => {
        const Icon = item.icon;
        const active = isItemActive(path, item);
        return (
          <SidebarMenuItem key={`${item.title}-${item.url}`}>
            <SidebarMenuButton
              isActive={active}
              onClick={() => onGo(item.url)}
              tooltip={item.title}
              className={itemClass}
            >
              <Icon
                className={cn(
                  "size-4 stroke-[1.75]",
                  active
                    ? "text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/55"
                )}
                aria-hidden
              />
              <span className="truncate">{item.title}</span>
            </SidebarMenuButton>
            {item.badge ? (
              <SidebarMenuBadge className="right-1.5 top-1 h-4.5 min-w-4 rounded-full bg-muted px-1 text-[10px] font-semibold text-muted-foreground">
                {item.badge}
              </SidebarMenuBadge>
            ) : null}
          </SidebarMenuItem>
        );
      })}
    </SidebarMenu>
  );
}

export default function PlatformMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const permissions = usePermissions();
  const { hasProfil, isRecruiter } = useMySpace();
  const { data: badges } = useGetActivityBadgesQuery(undefined, {
    pollingInterval: 30000,
  });

  const go = (url: string) => {
    navigate(url);
    if (isMobile) setOpenMobile(false);
  };

  const path = location.pathname;

  const principalItems: NavItem[] = [
    {
      title: "Forum",
      url: "/",
      icon: Home,
      match: (p) =>
        p === "/" ||
        (p.startsWith("/forum/") &&
          !p.startsWith("/forum/profil") &&
          !p.startsWith("/forum/communautes") &&
          !p.startsWith("/forum/chaines") &&
          !p.startsWith("/forum/favoris")),
    },
    {
      title: "Communautés",
      url: "/forum/communautes",
      icon: Users,
      badge: formatBadge(badges?.communautes),
    },
    {
      title: "Chaînes",
      url: "/forum/chaines",
      icon: Radio,
      badge: formatBadge(badges?.chaines),
    },
    {
      title: "Messages",
      url: "/messages",
      icon: Mail,
      badge: formatBadge(badges?.messages),
    },
    {
      title: "Favoris",
      url: "/forum/favoris",
      icon: Bookmark,
    },
    {
      title: "Mon compte",
      url: "/forum/profil/me",
      icon: UserRound,
      match: (p) => p.startsWith("/forum/profil"),
    },
  ];

  const marketplaceItems: NavItem[] = [
    {
      title: "Tableau de bord",
      url: "/marketplace",
      icon: LayoutDashboard,
      exact: true,
    },
    {
      title: "Mon profil pro",
      url: "/marketplace/profile",
      icon: UserRound,
    },
    ...(hasProfil
      ? [
          {
            title: "Offres pour moi",
            url: "/marketplace/offers",
            icon: Briefcase,
          },
          {
            title: "Mes candidatures",
            url: "/marketplace/applications",
            icon: ClipboardList,
          },
          {
            title: "Réseau",
            url: "/marketplace/network",
            icon: Network,
          },
          {
            title: "Mes disponibilités",
            url: "/marketplace/availability",
            icon: CalendarDays,
          },
          {
            title: "Mon CV",
            url: "/marketplace/cv",
            icon: FileText,
          },
        ]
      : []),
    ...(isRecruiter
      ? [
          {
            title: "Mes offres",
            url: "/marketplace/my-offers",
            icon: Store,
          },
          {
            title: "Talents",
            url: "/marketplace/talents",
            icon: UsersRound,
            exact: true,
          },
          {
            title: "Vivier",
            url: "/marketplace/talents/pool",
            icon: Users,
          },
        ]
      : []),
  ];

  const canAdministerMarketplace = MARKETPLACE_ADMIN_PAGES.some(
    (page) => permissions[page.permission]
  );

  if (canAdministerMarketplace) {
    marketplaceItems.push({
      title: "Administration",
      url: "/admin/marketplace",
      icon: Shield,
    });
  }

  const hubItems: NavItem[] = [
    {
      title: "Explorer les projets",
      url: "/hub/projects",
      icon: FolderKanban,
    },
  ];

  return (
    <>
      <SidebarGroup className="p-0 px-1">
        <SidebarGroupLabel className={sectionLabelClass}>
          Principal
        </SidebarGroupLabel>
        <NavList items={principalItems} path={path} onGo={go} />
      </SidebarGroup>

      <Separator className="mx-3 bg-sidebar-border/70" />

      <SidebarGroup className="p-0 px-1">
        <SidebarGroupLabel className={sectionLabelClass}>
          Marketplace
        </SidebarGroupLabel>
        <NavList items={marketplaceItems} path={path} onGo={go} />
      </SidebarGroup>

      <Separator className="mx-3 bg-sidebar-border/70" />

      <SidebarGroup className="p-0 px-1">
        <SidebarGroupLabel className={sectionLabelClass}>
          DevStreet Hub
        </SidebarGroupLabel>
        <NavList items={hubItems} path={path} onGo={go} />
      </SidebarGroup>
    </>
  );
}
