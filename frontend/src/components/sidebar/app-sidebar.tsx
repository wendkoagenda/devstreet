import * as React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useAuthSlice } from "@/models/auth/slice";
import AppSidebarFooter from "./components/app-sidebar-footer";
import AppSidebarMainMenu from "./components/app-sidebar-main-menu";
import AppSidebarHeader from "./components/app-sidebar-header";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const loadSession = useAuthSlice((state) => state.loadSession);

  React.useEffect(() => {
    if (!isAuthenticated) return;
    void loadSession();
    const handleFocus = () => {
      void loadSession();
    };
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, [isAuthenticated, loadSession]);

  return (
    <Sidebar
      variant="floating"
      collapsible="offcanvas"
      {...props}
      className="font-sans text-sidebar-foreground antialiased"
    >
      <SidebarHeader className="p-0">
        <AppSidebarHeader />
      </SidebarHeader>
      <SidebarContent className="gap-0 overflow-x-hidden overflow-y-auto px-2 py-2 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <AppSidebarMainMenu />
      </SidebarContent>
      <SidebarRail />
      <SidebarFooter className="p-2 pt-0">
        <AppSidebarFooter />
      </SidebarFooter>
    </Sidebar>
  );
}
