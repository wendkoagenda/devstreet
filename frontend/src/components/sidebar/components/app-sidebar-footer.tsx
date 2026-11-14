import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar";

export default function AppSidebarFooter() {
  return (
    <SidebarMenu className="gap-2 border-t border-sidebar-border/70 px-1 pb-1 pt-3">
      <SidebarMenuItem className="flex items-center gap-1 px-1">
        <LanguageToggle />
        <ModeToggle />
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
