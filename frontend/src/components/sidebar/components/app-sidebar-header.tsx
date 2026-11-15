import { BrandLogo } from "@/components/brand/brand-logo";
import {
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { t } from "i18next";
import { Link } from "react-router-dom";

export default function AppSidebarHeader() {
  const { isMobile, setOpenMobile } = useSidebar();

  const handleGoToHome = () => {
    if (isMobile) setOpenMobile(false);
  };

  return (
    <SidebarHeader className="rounded-t-2xl border-b border-sidebar-border/70 px-3 pb-3 pt-4">
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton
            size="lg"
            asChild
            className="h-11 rounded-xl px-2.5 hover:bg-sidebar-accent/60 active:bg-sidebar-accent/60"
          >
            <Link
              to="/"
              onClick={handleGoToHome}
              aria-label={t("sidebar.brand_home")}
              className="gap-2.5"
            >
              <BrandLogo variant="mark" className="size-8 shrink-0" />
              <span className="flex min-w-0 flex-col leading-none">
                <span className="truncate text-[15px] font-bold tracking-tight text-foreground">
                  {t("sidebar.brand")}
                </span>
                <span className="mt-1 font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
                  {t("sidebar.brand_badge")}
                </span>
              </span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
  );
}
