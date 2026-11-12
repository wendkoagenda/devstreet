import {
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { t } from "i18next";
import { Terminal } from "lucide-react";
import { Link } from "react-router-dom";

export default function AppSidebarHeader() {
  const { isMobile, setOpenMobile } = useSidebar();

  const handleGoToHome = () => {
    if (isMobile) setOpenMobile(false);
  };

  return (
    <SidebarHeader className="border-b border-sidebar-border px-3 py-3">
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" asChild className="hover:bg-transparent active:bg-transparent">
            <Link to="/hub/projects" onClick={handleGoToHome} aria-label={t("sidebar.brand_home")}>
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
                <Terminal aria-hidden className="h-[18px] w-[18px]" />
              </span>
              <span className="text-lg font-bold tracking-tight text-foreground">
                {t("sidebar.brand")}
              </span>
              <span className="rounded border border-brand-soft-border bg-brand-soft px-1.5 py-0.5 font-mono text-[10px] font-bold text-brand-strong">
                {t("sidebar.brand_badge")}
              </span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
  );
}
