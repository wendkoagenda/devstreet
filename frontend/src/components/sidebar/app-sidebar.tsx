import * as React from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import AppSidebarFooter from "./components/app-sidebar-footer";
import AppSidebarMainMenu from "./components/app-sidebar-main-menu";
import AppSidebarHeader from "./components/app-sidebar-header";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar {...props}>
      {/* Header */}
      <SidebarHeader>
        <AppSidebarHeader />
      </SidebarHeader>
      {/* Content */}
      <SidebarContent>
        <AppSidebarMainMenu />
      </SidebarContent>
      <SidebarRail />
      {/* Footer */}
      <SidebarFooter>
        <AppSidebarFooter />
      </SidebarFooter>
    </Sidebar>
  );
}
