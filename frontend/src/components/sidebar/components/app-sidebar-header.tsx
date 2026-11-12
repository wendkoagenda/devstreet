import {
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { t } from "i18next";
import { useNavigate } from "react-router-dom";

export default function AppSidebarHeader() {
  const navigate = useNavigate();
  const { isMobile, setOpenMobile } = useSidebar();

  const handleGoToHome = () => {
    navigate("/");
    if (isMobile) setOpenMobile(false);
  };

  return (
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" asChild>
            <a onClick={handleGoToHome}>
              <div className="flex h-8 items-center justify-center text-sidebar-primary-foreground">
                <img src={t("app.logo")} alt="Logo devstreet" className="h-5 w-auto object-contain" />
              </div>
              <div className="flex flex-col gap-0.5 leading-none">
                <span className="font-semibold">{t("app.name")}</span>
                <span className="">{t("app.version")}</span>
              </div>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
  );
}
