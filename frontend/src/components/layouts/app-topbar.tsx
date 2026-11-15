import { profilePath } from "@/helpers/routes/profile-path";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, Search, SendHorizontal, Terminal, UserRound } from "lucide-react";
import { t } from "i18next";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SidebarTrigger } from "@/components/ui/sidebar";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";
import { cn } from "@/lib/utils";
import { useAuth } from "@/models/auth/hooks/useAuth";
import { useAuthSlice } from "@/models/auth/slice";
import { useAccountType } from "@/models/auth/account-type/use-account-type";
import { ForumAvatar } from "@/models/forum/components/forum-avatar";
import { ResumeNotificationBell } from "@/models/forum/components/resume-notification-bell";
import { GlobalSearchDialog } from "./global-search-dialog";

function isMacPlatform() {
  if (typeof navigator === "undefined") return false;
  return /Mac|iPhone|iPad|iPod/i.test(navigator.platform || navigator.userAgent);
}

export function AppTopbar() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const user = useAuthSlice((state) => state.user);
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const authReady = useAuthSlice((state) => state.isInitialized);
  const { showCommunity, homePath } = useAccountType();
  const [searchOpen, setSearchOpen] = useState(false);
  const shortcutLabel = isMacPlatform() ? "⌘K" : "Ctrl K";

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const displayName = user?.full_name || user?.username || t("topbar.profile_fallback");

  const handlePublish = () => {
    navigate("/?publish=1", { flushSync: true });
  };

  const handleLogout = async () => {
    try {
      // Attendre la fin de la déconnexion : sinon on arrive sur /login encore « connecté »
      // et PublicRoute renvoie vers le forum jusqu'au prochain refresh.
      await logout();
      navigate("/welcome", { replace: true });
      CreationSuccessSonner(t("auth.logout_success"));
    } catch (error) {
      console.error("Logout failed:", error);
      CreationErrorSonner(t("auth.logout_error"));
    }
  };

  const handleGoToProfile = () => {
    if (user?.username) navigate(profilePath(user.username));
    else navigate("/profil/me");
  };

  return (
    <>
      <header className="sticky top-0 z-20 bg-background/80 p-3 pb-2 backdrop-blur-md supports-[backdrop-filter]:bg-background/70 sm:p-4 sm:pb-3">
        <div
          className={cn(
            "mx-auto flex h-14 max-w-7xl items-center gap-2 rounded-2xl border border-brand-soft-border bg-card px-2.5 shadow-[0_1px_2px_hsl(var(--foreground)/0.04)] sm:gap-3 sm:px-3"
          )}
        >
          <div className="flex min-w-0 shrink-0 items-center gap-1.5 sm:gap-2">
            <SidebarTrigger className="rounded-xl text-muted-foreground hover:text-foreground md:hidden" />
            <Link
              to={homePath}
              className="flex min-w-0 items-center gap-2 rounded-xl px-1 py-1 transition-colors hover:bg-muted/50"
              aria-label={t("topbar.home_aria")}
            >
              <span className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-foreground text-background">
                <Terminal className="size-4" aria-hidden />
              </span>
              <span className="hidden min-w-0 items-baseline gap-1.5 sm:flex">
                <span className="truncate text-[15px] font-bold tracking-tight text-foreground">
                  {t("sidebar.brand")}
                </span>
                <span className="shrink-0 font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
                  {t("topbar.beta")}
                </span>
              </span>
            </Link>
          </div>

          <button
            type="button"
            data-tour="topbar-search"
            onClick={() => setSearchOpen(true)}
            className={cn(
              "group flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-transparent bg-muted/60 px-2.5 py-2 text-left transition-colors sm:px-3",
              "hover:border-brand-soft-border hover:bg-muted"
            )}
            aria-label={t("topbar.search_aria")}
          >
            <Search
              className="size-3.5 shrink-0 text-muted-foreground"
              aria-hidden
            />
            <span className="min-w-0 flex-1 truncate text-sm text-muted-foreground">
              <span className="hidden md:inline">
                {t("topbar.search_placeholder")}
              </span>
              <span className="hidden min-[380px]:inline md:hidden">
                {t("topbar.search_short")}
              </span>
            </span>
            <kbd className="hidden shrink-0 rounded-md border border-border bg-card px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground md:inline-block">
              {shortcutLabel}
            </kbd>
          </button>

          <div className="flex shrink-0 items-center gap-0.5 sm:gap-1.5">
            {showCommunity ? (
              <Button
                type="button"
                size="sm"
                data-tour="topbar-publish"
                onClick={handlePublish}
                aria-label={t("topbar.publish_aria")}
                className="h-9 gap-1.5 rounded-xl bg-brand px-2.5 text-brand-foreground hover:bg-brand-strong sm:px-3"
              >
                <span className="hidden sm:inline">{t("topbar.publish")}</span>
                <SendHorizontal className="size-3.5" aria-hidden />
              </Button>
            ) : null}

            <ResumeNotificationBell indicator="dot" />

            {!authReady ? (
              <div
                className="ml-0.5 size-8 animate-pulse rounded-full bg-muted"
                aria-hidden
              />
            ) : isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    type="button"
                    className="relative ml-0.5 rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/35"
                    aria-label={t("topbar.account_menu_aria", { name: displayName })}
                  >
                    <ForumAvatar
                      name={displayName}
                      photo={user?.photo}
                      size="sm"
                      tone="soft"
                    />
                    <span
                      className="absolute bottom-0 right-0 size-2.5 rounded-full border-2 border-card bg-success"
                      aria-hidden
                    />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  sideOffset={8}
                  className="w-52 rounded-xl"
                >
                  <DropdownMenuItem
                    onClick={handleGoToProfile}
                    className="gap-2"
                  >
                    <UserRound className="size-4" />
                    {t("topbar.my_profile")}
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
                size="sm"
                className="rounded-xl"
                onClick={() => navigate("/login", { flushSync: true })}
              >
                {t("login")}
              </Button>
            )}
          </div>
        </div>
      </header>

      <GlobalSearchDialog open={searchOpen} onOpenChange={setSearchOpen} />
    </>
  );
}
