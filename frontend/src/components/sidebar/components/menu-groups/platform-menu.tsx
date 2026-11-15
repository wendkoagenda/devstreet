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
  Plus,
  Radio,
  Shield,
  Store,
  Users,
  UsersRound,
  type LucideIcon,
} from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";
import { usePermissions } from "@/hooks/use-permissions";
import { useAuthSlice } from "@/models/auth/slice";
import { useAccountType } from "@/models/auth/account-type/use-account-type";
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
  "h-8 gap-2.5 rounded-lg px-2.5 font-sans text-sm font-medium leading-5 text-sidebar-foreground transition-colors duration-150 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:font-semibold data-[active=true]:text-sidebar-accent-foreground data-[active=true]:shadow-[inset_0_0_0_1px_hsl(var(--sidebar-border))]";

const sectionLabelClass =
  "mb-0.5 h-auto px-2.5 py-0.5 font-sans text-[10px] font-medium uppercase leading-4 tracking-[0.14em] text-muted-foreground";

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
                  "size-4 stroke-2",
                  active
                    ? "text-sidebar-accent-foreground"
                    : "text-muted-foreground"
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
        className="flex w-full items-center justify-between rounded-md px-2.5 py-1 font-sans text-[11px] font-medium leading-4 text-muted-foreground transition-colors hover:text-sidebar-foreground"
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
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, setOpenMobile } = useSidebar();
  const permissions = usePermissions();
  const { hasProfil, isRecruiter, company } = useMySpace();
  const { showDevSpace, showEntrepriseSpace, showCommunity, missingType } = useAccountType();
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const userId = useAuthSlice((state) => state.user?.id ?? null);
  const { data: badges } = useGetActivityBadgesQuery(undefined, {
    pollingInterval: 30000,
  });

  const go = (url: string) => {
    // flushSync : évite le décalage URL / contenu (React Router 7 wrappe sinon en startTransition).
    navigate(url, { flushSync: true });
    if (isMobile) setOpenMobile(false);
  };

  const path = location.pathname;
  const search = location.search;
  const myProjectsUrl =
    userId != null ? `/hub/projects?owner=${userId}` : "/hub/projects";

  const principalItems: NavItem[] = [
    {
      title: t("sidebar.forum"),
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
      title: t("sidebar.communities"),
      url: "/forum/communautes",
      icon: Users,
      tourId: "nav-communities",
      badge: formatBadge(badges?.communautes),
    },
    {
      title: t("sidebar.channels"),
      url: "/forum/chaines",
      icon: Radio,
      tourId: "nav-channels",
      badge: formatBadge(badges?.chaines),
    },
    {
      title: t("sidebar.messages"),
      url: "/messages",
      icon: Mail,
      tourId: "nav-messages",
      badge: formatBadge(badges?.messages),
    },
    {
      title: t("sidebar.favorites"),
      url: "/forum/favoris",
      icon: Bookmark,
      tourId: "nav-favorites",
    },
  ];

  // Général : visible par tous.
  const generalItems: NavItem[] = [
    {
      title: t("sidebar.explore_offers"),
      url: "/marketplace/offers",
      icon: Briefcase,
    },
  ];

  const canAdministerMarketplace = MARKETPLACE_ADMIN_PAGES.some(
    (page) => permissions[page.permission]
  );

  if (canAdministerMarketplace) {
    generalItems.push({
      title: t("sidebar.administration"),
      url: "/admin/marketplace",
      icon: Shield,
    });
  }

  // Espace dev : pour les membres qui ont un profil dev
  const devItems: NavItem[] = [
    {
      title: t("sidebar.network"),
      url: "/marketplace/network",
      icon: Network,
    },
    {
      title: t("sidebar.my_applications"),
      url: "/marketplace/applications",
      icon: ClipboardList,
    },
    {
      title: t("sidebar.my_availability"),
      url: "/marketplace/availability",
      icon: CalendarDays,
    },
    {
      title: t("sidebar.my_cv"),
      url: "/marketplace/cv",
      icon: FileText,
    },
  ];

  // Entreprise : pour les membres qui ont un profil entreprise
  const entrepriseItems: NavItem[] = [
    {
      title: t("sidebar.my_offers"),
      url: "/marketplace/my-offers",
      icon: Store,
    },
    {
      title: t("sidebar.talents"),
      url: "/marketplace/talents",
      icon: UsersRound,
      exact: true,
    },
    {
      title: t("sidebar.pool"),
      url: "/marketplace/talents/pool",
      icon: Users,
    },
  ];

  const hubItems: NavItem[] = [
    {
      title: t("sidebar.explore_projects"),
      url: "/hub/projects",
      icon: FolderKanban,
      match: (p, s) =>
        p.startsWith("/hub/projects") &&
        !new URLSearchParams(s).get("owner"),
    },
    ...(isAuthenticated && userId != null
      ? [
          {
            title: t("sidebar.my_projects"),
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

  // Compte entreprise seule : pas de forum ni de projets, mais la messagerie reste accessible
  const messagesOnlyItems = principalItems.filter((item) => item.tourId === "nav-messages");

  // Invitation à ajouter le type manquant (relance l'assistant pour ce seul type)
  const addTypeItem: NavItem | null =
    missingType === "entreprise"
      ? {
          title: t("sidebar.create_company"),
          url: "/onboarding?add=entreprise&resume=1",
          icon: Plus,
        }
      : missingType === "dev"
        ? {
            title: t("sidebar.create_dev_profile"),
            url: "/onboarding?add=dev&resume=1",
            icon: Plus,
          }
        : null;

  return (
    <>
      {showCommunity ? (
        <SidebarGroup className="p-0 px-1">
          <SidebarGroupLabel className={sectionLabelClass}>
            {t("sidebar.principal")}
          </SidebarGroupLabel>
          <NavList items={principalItems} path={path} search={search} onGo={go} />
        </SidebarGroup>
      ) : (
        <SidebarGroup className="p-0 px-1">
          <NavList items={messagesOnlyItems} path={path} search={search} onGo={go} />
        </SidebarGroup>
      )}

      <Separator className="mx-3 bg-sidebar-border/70" />

      <SidebarGroup className="p-0 px-1" data-tour="nav-marketplace">
        <SidebarGroupLabel className={sectionLabelClass}>
          {t("sidebar.marketplace")}
        </SidebarGroupLabel>
        <MenuSection
          id="general"
          label={t("sidebar.general")}
          items={generalItems}
          path={path}
          search={search}
          onGo={go}
        />
        {showDevSpace ? (
          <MenuSection
            id="dev"
            label={t("sidebar.dev_space")}
            items={devItems}
            invite={
              hasProfil
                ? undefined
                : {
                    title: t("sidebar.create_dev_profile"),
                    url: "/profil/me?section=dev",
                    icon: Code2,
                  }
            }
            path={path}
            search={search}
            onGo={go}
          />
        ) : null}
        {showEntrepriseSpace ? (
          <MenuSection
            id="entreprise"
            label={company?.name ?? t("sidebar.my_company")}
            items={entrepriseItems}
            invite={
              isRecruiter
                ? undefined
                : {
                    title: t("sidebar.create_company"),
                    url: "/profil/me?section=entreprise",
                    icon: Building2,
                  }
            }
            path={path}
            search={search}
            onGo={go}
          />
        ) : null}
        {addTypeItem ? (
          <div className="mt-1.5">
            <NavList items={[addTypeItem]} path={path} search={search} onGo={go} />
          </div>
        ) : null}
      </SidebarGroup>

      {showCommunity ? (
        <>
          <Separator className="mx-3 bg-sidebar-border/70" />

          <SidebarGroup className="p-0 px-1" data-tour="nav-projects">
            <SidebarGroupLabel className={sectionLabelClass}>
              {t("sidebar.projects")}
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
  const { t } = useTranslation();
  const selected = path === "/" ? activeTag : null;

  return (
    <div className="space-y-1 px-2.5">
      <p className={sectionLabelClass}>{t("sidebar.followed_tags")}</p>
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
