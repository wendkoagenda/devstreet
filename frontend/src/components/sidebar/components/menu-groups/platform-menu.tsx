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
  Building2,
  CalendarDays,
  ChevronDown,
  ClipboardList,
  Code2,
  FileText,
  FolderKanban,
  FolderOpen,
  Home,
  Mail,
  Network,
  Radio,
  Shield,
  Store,
  Users,
  UsersRound,
  type LucideIcon,
} from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { usePermissions } from "@/hooks/use-permissions";
import { useAuthSlice } from "@/models/auth/slice";
import { MARKETPLACE_ADMIN_PAGES } from "@/models/marketplace-space/admin-pages";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { useGetActivityBadgesQuery } from "@/models/forum/api";
import { FavorisTagQuickSelect } from "@/models/forum/components/favoris-tag-quick-select";

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
  /** Ancre du tour guidé (data-tour). */
  tourId?: string;
  match?: (path: string, search: string) => boolean;
};

const itemClass =
  "h-8 gap-2.5 rounded-lg px-2.5 text-[13px] font-medium text-sidebar-foreground/80 transition-colors duration-150 hover:bg-sidebar-accent/80 hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:font-semibold data-[active=true]:text-sidebar-accent-foreground data-[active=true]:shadow-[inset_0_0_0_1px_hsl(var(--sidebar-border))]";

const sectionLabelClass =
  "mb-0.5 h-auto px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground/80";

function isItemActive(path: string, search: string, item: NavItem) {
  if (item.match) return item.match(path, search);
  if (path === item.url) return true;
  if (item.exact) return false;
  return path.startsWith(`${item.url}/`);
}

function NavList({
  items,
  path,
  search,
  onGo,
}: {
  items: NavItem[];
  path: string;
  search: string;
  onGo: (url: string) => void;
}) {
  return (
    <SidebarMenu className="gap-0.5">
      {items.map((item) => {
        const Icon = item.icon;
        const active = isItemActive(path, search, item);
        return (
          <SidebarMenuItem
            key={`${item.title}-${item.url}`}
            data-tour={item.tourId}
          >
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

const MENU_SECTION_STORAGE_PREFIX = "sidebar.marketplace.";

function isSectionOpen(id: string): boolean {
  let stored: string | null = null;
  try {
    stored = window.localStorage.getItem(MENU_SECTION_STORAGE_PREFIX + id);
  } catch (error) {
    console.warn("Préférence du menu illisible (stockage bloqué), sections ouvertes par défaut", error);
  }
  return stored !== "closed";
}

/**
 * Sous-section du groupe Marketplace (Général, espace dev, entreprise) : un titre repliable, l'état est mémorisé.
 * Si le membre n'a pas le profil correspondant, la section se réduit à une invitation à le créer.
 */
function MenuSection({
  id,
  label,
  items,
  invite,
  path,
  search,
  onGo,
}: {
  id: string;
  label: string;
  items: NavItem[];
  /** Affichée à la place des éléments quand le membre n'a pas ce profil. */
  invite?: NavItem;
  path: string;
  search: string;
  onGo: (url: string) => void;
}) {
  const [open, setOpen] = useState(() => isSectionOpen(id));

  const toggle = () => {
    setOpen((current) => {
      const next = !current;
      try {
        window.localStorage.setItem(MENU_SECTION_STORAGE_PREFIX + id, next ? "open" : "closed");
      } catch (error) {
        console.warn("Préférence du menu non mémorisée (stockage bloqué)", error);
      }
      return next;
    });
  };

  return (
    <div className="mt-1.5">
      <button
        type="button"
        onClick={toggle}
        aria-expanded={open}
        className="flex w-full items-center justify-between rounded-md px-2.5 py-1 text-[11px] font-semibold text-sidebar-foreground/70 transition-colors hover:text-sidebar-foreground"
      >
        <span className="truncate">{label}</span>
        <ChevronDown
          className={cn("size-3 shrink-0 transition-transform", !open && "-rotate-90")}
          aria-hidden
        />
      </button>
      {open ? (
        <NavList
          items={invite ? [invite] : items}
          path={path}
          search={search}
          onGo={onGo}
        />
      ) : null}
    </div>
  );
}

export default function PlatformMenu() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const permissions = usePermissions();
  const { hasProfil, isRecruiter, company } = useMySpace();
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const userId = useAuthSlice((state) => state.user?.id ?? null);
  const { data: badges } = useGetActivityBadgesQuery(undefined, {
    pollingInterval: 30000,
  });

  const go = (url: string) => {
    navigate(url);
    if (isMobile) setOpenMobile(false);
  };

  const path = location.pathname;
  const search = location.search;
  const myProjectsUrl =
    userId != null ? `/hub/projects?owner=${userId}` : "/hub/projects";

  const principalItems: NavItem[] = [
    {
      title: "Forum",
      url: "/",
      icon: Home,
      tourId: "nav-forum",
      match: (p) =>
        p === "/" ||
        (p.startsWith("/forum/") &&
          !p.startsWith("/forum/communautes") &&
          !p.startsWith("/forum/chaines") &&
          !p.startsWith("/forum/favoris")),
    },
    {
      title: "Communautés",
      url: "/forum/communautes",
      icon: Users,
      tourId: "nav-communities",
      badge: formatBadge(badges?.communautes),
    },
    {
      title: "Chaînes",
      url: "/forum/chaines",
      icon: Radio,
      tourId: "nav-channels",
      badge: formatBadge(badges?.chaines),
    },
    {
      title: "Messages",
      url: "/messages",
      icon: Mail,
      tourId: "nav-messages",
      badge: formatBadge(badges?.messages),
    },
    {
      title: "Favoris",
      url: "/forum/favoris",
      icon: Bookmark,
      tourId: "nav-favorites",
    },
  ];

  // Général : visible par tous.
  const generalItems: NavItem[] = [
    {
      title: "Explorer les offres",
      url: "/marketplace/offers",
      icon: Briefcase,
    },
  ];

  const canAdministerMarketplace = MARKETPLACE_ADMIN_PAGES.some(
    (page) => permissions[page.permission]
  );

  if (canAdministerMarketplace) {
    generalItems.push({
      title: "Administration",
      url: "/admin/marketplace",
      icon: Shield,
    });
  }

  // Espace dev : pour les membres qui ont un profil dev
  const devItems: NavItem[] = [
    {
      title: "Réseau",
      url: "/marketplace/network",
      icon: Network,
    },
    {
      title: "Mes candidatures",
      url: "/marketplace/applications",
      icon: ClipboardList,
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
  ];

  // Entreprise : pour les membres qui ont un profil entreprise
  const entrepriseItems: NavItem[] = [
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
  ];

  const hubItems: NavItem[] = [
    {
      title: "Explorer les projets",
      url: "/hub/projects",
      icon: FolderKanban,
      match: (p, s) =>
        p.startsWith("/hub/projects") &&
        !new URLSearchParams(s).get("owner"),
    },
    ...(isAuthenticated && userId != null
      ? [
          {
            title: "Mes projets",
            url: myProjectsUrl,
            icon: FolderOpen,
            match: (p: string, s: string) =>
              p.startsWith("/hub/projects") &&
              new URLSearchParams(s).get("owner") === String(userId),
          },
        ]
      : []),
  ];

  const activeTag = new URLSearchParams(search).get("tag");

  return (
    <>
      <SidebarGroup className="p-0 px-1">
        <SidebarGroupLabel className={sectionLabelClass}>
          Principal
        </SidebarGroupLabel>
        <NavList items={principalItems} path={path} search={search} onGo={go} />
      </SidebarGroup>

      <Separator className="mx-3 bg-sidebar-border/70" />

      <SidebarGroup className="p-0 px-1" data-tour="nav-marketplace">
        <SidebarGroupLabel className={sectionLabelClass}>
          Marketplace
        </SidebarGroupLabel>
        <MenuSection
          id="general"
          label="Général"
          items={generalItems}
          path={path}
          search={search}
          onGo={go}
        />
        <MenuSection
          id="dev"
          label="Mon espace dev"
          items={devItems}
          invite={
            hasProfil
              ? undefined
              : { title: "Créer mon profil dev", url: "/profil/me?section=dev", icon: Code2 }
          }
          path={path}
          search={search}
          onGo={go}
        />
        <MenuSection
          id="entreprise"
          label={company?.name ?? "Mon entreprise"}
          items={entrepriseItems}
          invite={
            isRecruiter
              ? undefined
              : { title: "Créer mon entreprise", url: "/profil/me?section=entreprise", icon: Building2 }
          }
          path={path}
          search={search}
          onGo={go}
        />
      </SidebarGroup>

      <Separator className="mx-3 bg-sidebar-border/70" />

      <SidebarGroup className="p-0 px-1" data-tour="nav-projects">
        <SidebarGroupLabel className={sectionLabelClass}>
          Projets
        </SidebarGroupLabel>
        <NavList items={hubItems} path={path} search={search} onGo={go} />
      </SidebarGroup>

      {isAuthenticated ? (
        <>
          <Separator className="mx-3 bg-sidebar-border/70" />
          <SidebarGroup className="p-0 px-1">
            <HubMesFavoris activeTag={activeTag} path={path} onGo={go} />
          </SidebarGroup>
        </>
      ) : null}
    </>
  );
}

function HubMesFavoris({
  activeTag,
  path,
  onGo,
}: {
  activeTag: string | null;
  path: string;
  onGo: (url: string) => void;
}) {
  const selected = path === "/" ? activeTag : null;

  return (
    <div className="space-y-1 px-2.5">
      <p className={sectionLabelClass}>Tags suivis</p>
      <FavorisTagQuickSelect
        variant="sidebar"
        activeSlug={selected}
        onSelect={(slug) => {
          if (!slug) {
            onGo("/");
            return;
          }
          onGo(`/?tag=${encodeURIComponent(slug)}`);
        }}
      />
    </div>
  );
}
