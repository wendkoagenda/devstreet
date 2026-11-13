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
import { t } from "i18next";
import { useLocation, useNavigate } from "react-router-dom";

const itemClass =
  "h-8 gap-2.5 rounded-lg px-2.5 text-[13px] font-medium text-sidebar-foreground/80 transition-colors duration-150 hover:bg-sidebar-accent/80 hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:font-semibold data-[active=true]:text-sidebar-accent-foreground data-[active=true]:shadow-[inset_0_0_0_1px_hsl(var(--sidebar-border))]";

const sectionLabelClass =
  "mb-0.5 h-auto px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground/80";

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
  ].filter((item) => item.permission);

  if (menuItems.length === 0) {
    return null;
  }

  return (
    <>
      <Separator className="mx-3 bg-sidebar-border/70" />
      <SidebarGroup className="p-0 px-1">
        <SidebarGroupLabel className={sectionLabelClass}>
          Administration
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
                    navigate(item.url);
                    if (isMobile) setOpenMobile(false);
                  }}
                  tooltip={item.title}
                  className={itemClass}
                >
                  <Icon
                    aria-hidden
                    className={cn(
                      "size-4 stroke-[1.75]",
                      isActive
                        ? "text-sidebar-accent-foreground"
                        : "text-sidebar-foreground/55"
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
