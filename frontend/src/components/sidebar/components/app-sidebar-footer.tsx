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
import { Button } from "@/components/ui/button";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";
import { truncateTitle } from "@/helpers/displayers/truncate-title";
import { useAuth } from "@/models/auth/hooks/useAuth";
import { useAuthSlice } from "@/models/auth/slice";
import { t } from "i18next";
import { ChevronUp, LogOut, UserRound } from "lucide-react";
import { useNavigate } from "react-router-dom";

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
}

export default function AppSidebarFooter() {
  const userFullName = useAuthSlice((state) => state.user?.full_name) ?? "";
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    try {
      logout();
      navigate("/login");
      CreationSuccessSonner(t("auth.logout_success"));
    } catch (error) {
      console.error("Logout failed:", error);
      CreationErrorSonner(t("auth.logout_error"));
    }
  };

  const currentUserId = useAuthSlice((state) => state.user?.id);

  const handleGoToMyAccount = () => {
    navigate("/my-account");
  };

  const handleGoToProfile = () => {
    if (currentUserId) navigate(`/forum/profil/${currentUserId}`);
    else navigate("/forum/profil/me");
  };

  return (
    <SidebarMenu className="gap-2 border-t border-sidebar-border/70 px-1 pb-1 pt-3">
      <SidebarMenuItem className="flex items-center gap-1 px-1">
        <ModeToggle />
        <LanguageToggle />
      </SidebarMenuItem>

      <SidebarMenuItem>
        {isAuthenticated ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                className="flex w-full items-center gap-2.5 rounded-xl px-2 py-2 text-left transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted font-mono text-[11px] font-semibold text-foreground ring-1 ring-sidebar-border">
                  {initials(userFullName)}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] font-medium leading-tight">
                    {truncateTitle(userFullName, 18)}
                  </span>
                  <span className="mt-0.5 block truncate font-mono text-[10px] uppercase tracking-wide text-muted-foreground">
                    Compte
                  </span>
                </span>
                <ChevronUp className="size-4 shrink-0 text-muted-foreground" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              side="top"
              align="start"
              className="w-[--radix-popper-anchor-width] rounded-xl"
            >
              <DropdownMenuItem onClick={handleGoToProfile} className="gap-2">
                <UserRound className="size-4" />
                Mon profil
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleGoToMyAccount} className="gap-2">
                <UserRound className="size-4" />
                {t("sidebar.my_account")}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="gap-2">
                <LogOut className="size-4" />
                {t("sidebar.disconnect")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button
            className="w-full rounded-xl"
            size="sm"
            onClick={() => navigate("/login")}
          >
            {t("login")}
          </Button>
        )}
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
