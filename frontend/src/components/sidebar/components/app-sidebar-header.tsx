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
            className="h-12 rounded-xl px-2.5 hover:bg-sidebar-accent/60 active:bg-sidebar-accent/60"
          >
            <Link
              to="/"
              onClick={handleGoToHome}
              aria-label={t("sidebar.brand_home")}
              className="gap-3"
            >
              <span className="relative inline-flex size-9 shrink-0 overflow-hidden rounded-full shadow-sm ring-1 ring-black/5">
                <BrandLogo
                  variant="mark"
                  className="size-full object-cover"
                />
              </span>
              <span className="min-w-0 truncate text-[15px] font-semibold tracking-[-0.02em] text-foreground">
                {t("sidebar.brand")}
              </span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
  );
}
