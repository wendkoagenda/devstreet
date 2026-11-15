import { Outlet } from "react-router-dom";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import React from "react";
import { SelinaPanel } from "@/models/ai/components/selina-panel";
import { SelinaProvider } from "@/models/ai/components/selina-provider";
import { useSelina } from "@/models/ai/components/use-selina";
import { cn } from "@/lib/utils";
import { AppTour } from "../onboarding/app-tour";
import { OnboardingReminder } from "../onboarding/onboarding-reminder";
import { AppSidebar } from "../sidebar/app-sidebar";
import { AppTopbar } from "./app-topbar";

function AppShell() {
  const selina = useSelina();
  const dockOpen = selina.open && selina.isAuthenticated && selina.canChat;

  return (
    <SidebarProvider
      defaultOpen
      style={{ "--sidebar-width": "17rem" } as React.CSSProperties}
    >
      <AppSidebar />

      <div
        className={cn(
          "min-w-0 flex-1 overflow-auto transition-[padding] duration-200",
          dockOpen && "lg:pr-[400px]"
        )}
      >
        <SidebarInset className="bg-background">
          <AppTopbar />
          <div className="flex flex-col gap-6 px-4 pb-6 pt-1 sm:px-6 sm:pb-8 lg:px-8 lg:pb-10">
            <OnboardingReminder />
            <Outlet />
          </div>
        </SidebarInset>
      </div>
      <AppTour />
      <SelinaPanel />
    </SidebarProvider>
  );
}

export default function AppLayout() {
  return (
    <SelinaProvider>
      <AppShell />
    </SelinaProvider>
  );
}
