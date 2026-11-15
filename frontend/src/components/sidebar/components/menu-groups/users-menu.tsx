import { Separator } from "@/components/ui/separator";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { usePermissions } from "@/hooks/use-permissions";
import { Icons } from "@/lib/constants/icons";
import { cn } from "@/lib/utils";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

const itemClass =
  "h-8 gap-2.5 rounded-lg px-2.5 font-sans text-sm font-medium leading-5 text-sidebar-foreground transition-colors duration-150 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:font-semibold data-[active=true]:text-sidebar-accent-foreground data-[active=true]:shadow-[inset_0_0_0_1px_hsl(var(--sidebar-border))]";

const sectionLabelClass =
  "mb-0.5 h-auto px-2.5 py-0.5 font-sans text-[10px] font-medium uppercase leading-4 tracking-[0.14em] text-muted-foreground";

export default function UsersMenu() {
  const { t } = useTranslation();
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
  ].filter((item) => item.permission);

  if (menuItems.length === 0) {
    return null;
  }

  return (
    <>
      <Separator className="mx-3 bg-sidebar-border/70" />
      <SidebarGroup className="p-0 px-1">
        <SidebarGroupLabel className={sectionLabelClass}>
          {t("sidebar.administration")}
        </SidebarGroupLabel>
        <SidebarMenu className="gap-0.5">
          {menuItems.map((item) => {
            const isActive = location.pathname === `/${item.url}`;
            const Icon = item.icon;

            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  isActive={isActive}
                  onClick={() => {
                    navigate(item.url, { flushSync: true });
                    if (isMobile) setOpenMobile(false);
                  }}
                  tooltip={item.title}
                  className={itemClass}
                >
                  <Icon
                    aria-hidden
                    className={cn(
                      "size-4 stroke-2",
                      isActive
                        ? "text-sidebar-accent-foreground"
                        : "text-muted-foreground"
                    )}
                  />
                  <span className="truncate">{item.title}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarGroup>
    </>
  );
}
