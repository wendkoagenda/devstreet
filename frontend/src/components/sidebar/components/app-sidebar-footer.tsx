import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar";

export default function AppSidebarFooter() {
  const { t } = useTranslation();

  return (
    <SidebarMenu className="gap-2 border-t border-sidebar-border/70 px-1 pb-1 pt-3">
      <SidebarMenuItem className="flex items-center gap-1 px-1">
        <Button variant="outline" size="icon" asChild>
          <Link to="/aide" aria-label={t("guide.open")} title={t("guide.open")}>
            <BookOpen className="h-[1.2rem] w-[1.2rem]" />
          </Link>
        </Button>
        <LanguageToggle />
        <ModeToggle />
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
