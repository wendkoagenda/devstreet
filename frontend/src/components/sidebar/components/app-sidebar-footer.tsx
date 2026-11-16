import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { BookOpen, ChevronUp, LogOut, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar";
import { useAccountMenu } from "@/hooks/use-account-menu";
import { ForumAvatar } from "@/models/forum/components/forum-avatar";

export default function AppSidebarFooter() {
  const { t } = useTranslation();
  const {
    user,
    isAuthenticated,
    authReady,
    displayName,
    goToProfile,
    handleLogout,
  } = useAccountMenu();

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

        {authReady && isAuthenticated ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className="relative overflow-visible"
                aria-label={t("topbar.account_menu_aria", { name: displayName })}
              >
                <ForumAvatar
                  name={displayName}
                  photo={user?.photo}
                  size="sm"
                  tone="soft"
                  className="h-5 w-5 text-[9px]"
                />
                <ChevronUp className="absolute -bottom-0.5 -right-0.5 size-2.5 text-muted-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" side="top" sideOffset={8} className="w-52 rounded-xl">
              <DropdownMenuItem onClick={goToProfile} className="gap-2">
                <UserRound className="size-4" />
                {t("topbar.my_profile")}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => void handleLogout()} className="gap-2">
                <LogOut className="size-4" />
                {t("sidebar.disconnect")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : null}
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
