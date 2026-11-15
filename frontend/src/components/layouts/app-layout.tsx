import { Outlet } from "react-router-dom";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import React from "react";
import { AppTour } from "../onboarding/app-tour";
import { OnboardingReminder } from "../onboarding/onboarding-reminder";
import { AppSidebar } from "../sidebar/app-sidebar";
import { AppTopbar } from "./app-topbar";

export default function AppLayout() {
  return (
    <SidebarProvider
      defaultOpen
      style={{ "--sidebar-width": "17rem" } as React.CSSProperties}
    >
      <AppSidebar />

      <div className="min-w-0 flex-1 overflow-auto">
        <SidebarInset className="bg-background">
          <AppTopbar />
          <div className="flex flex-col gap-6 px-4 pb-6 pt-1 sm:px-6 sm:pb-8 lg:px-8 lg:pb-10">
            <OnboardingReminder />
            <Outlet />
          </div>
        </SidebarInset>
      </div>
      <AppTour />
    </SidebarProvider>
  );
}
