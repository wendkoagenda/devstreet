import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Search, SendHorizontal, Sparkles } from "lucide-react";
import { t } from "i18next";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import { useAccountType } from "@/models/auth/account-type/use-account-type";
import { useSelina } from "@/models/ai/components/use-selina";
import { SelinaMascotte } from "@/models/ai/components/selina-mascotte";
import { ResumeNotificationBell } from "@/models/forum/components/resume-notification-bell";
import { GlobalSearchDialog } from "./global-search-dialog";

function isMacPlatform() {
  if (typeof navigator === "undefined") return false;
  return /Mac|iPhone|iPad|iPod/i.test(navigator.platform || navigator.userAgent);
}

export function AppTopbar() {
  const navigate = useNavigate();
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const authReady = useAuthSlice((state) => state.isInitialized);
  const { showCommunity } = useAccountType();
  const selina = useSelina();
  const [searchOpen, setSearchOpen] = useState(false);
  const [omnibar, setOmnibar] = useState("");
  const omnibarRef = useRef<HTMLInputElement | null>(null);
  const isMac = isMacPlatform();
  const searchShortcut = isMac ? "⌘K" : "Ctrl K";
  const selinaShortcut = isMac
    ? t("selina.omnibar_shortcut")
    : t("selina.omnibar_shortcut_win");

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
        return;
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "j") {
        event.preventDefault();
        omnibarRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const handlePublish = () => {
    navigate("/?publish=1", { flushSync: true });
  };

  const handleOmnibarSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const message = omnibar.trim();
    if (!message) return;
    if (!isAuthenticated) {
      navigate("/login", { flushSync: true });
      return;
    }
    setOmnibar("");
    await selina.send(message);
  };

  return (
    <>
      <header className="sticky top-0 z-20 w-full bg-background/85 px-4 pb-2 pt-3 backdrop-blur-md pointer-events-auto sm:px-6 sm:pt-4 lg:px-8">
        <nav
          className={cn(
            "flex w-full items-center justify-between gap-2 rounded-full border border-border/80 bg-card/95 px-2.5 py-1.5 shadow-floating backdrop-blur-xl transition-all duration-300 sm:gap-4",
            "hover:border-border"
          )}
          aria-label={t("topbar.home_aria")}
        >
          <div className="flex shrink-0 items-center gap-1 pl-0.5 sm:gap-2 sm:pl-1">
            <SidebarTrigger className="rounded-full text-muted-foreground hover:text-foreground md:hidden" />

            {!authReady ? (
              <div
                className="size-8 animate-pulse rounded-full bg-muted"
                aria-hidden
              />
            ) : isAuthenticated ? (
              <SelinaMascotte
                size="sm"
                interactive
                ariaLabel={t("selina.open")}
                onClick={() => selina.setOpen(true)}
                className="ring-1 ring-border/60"
              />
            ) : (
              <Button
                size="sm"
                className="rounded-full"
                onClick={() => navigate("/login", { flushSync: true })}
              >
                {t("login")}
              </Button>
            )}
          </div>

          <form
            className="relative mx-1 min-w-0 flex-1 max-w-xl sm:mx-2"
            onSubmit={handleOmnibarSubmit}
          >
            <label
              className={cn(
                "group relative flex w-full items-center justify-between gap-3 rounded-full border border-border/70 bg-muted/70 px-3.5 py-1.5 transition-all duration-200",
                "hover:border-brand/40 hover:bg-card hover:shadow-sm",
                "has-[:focus-visible]:border-brand/40 has-[:focus-visible]:bg-card has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-brand/30",
                selina.open && "border-brand/40 bg-card shadow-sm"
              )}
            >
              <span className="flex min-w-0 flex-1 items-center gap-2.5">
                <span
                  className={cn(
                    "inline-flex size-6 shrink-0 items-center justify-center rounded-full text-white shadow-sm",
                    "bg-gradient-to-tr from-brand to-brand-strong",
                    "animate-pulse-subtle motion-reduce:animate-none"
                  )}
                  aria-hidden
                >
                  <Sparkles className="size-3.5" />
                </span>
                <input
                  ref={omnibarRef}
                  type="text"
                  value={omnibar}
                  onChange={(event) => setOmnibar(event.target.value)}
                  placeholder={t("selina.omnibar_placeholder")}
                  aria-label={t("selina.omnibar_placeholder")}
                  disabled={selina.isBusy}
                  className={cn(
                    "min-w-0 flex-1 border-0 bg-transparent p-0 text-xs text-foreground outline-none placeholder:text-muted-foreground sm:text-sm",
                    "disabled:cursor-not-allowed disabled:opacity-60"
                  )}
                />
              </span>
              <span className="flex shrink-0 items-center gap-1.5">
                <span className="hidden items-center rounded-full bg-brand-soft px-2 py-0.5 text-[10px] font-semibold text-brand md:inline-flex">
                  {t("selina.omnibar_badge")}
                </span>
                <kbd className="hidden items-center rounded-md border border-border bg-card px-1.5 py-0.5 font-mono text-[11px] font-medium text-muted-foreground shadow-sm sm:inline-flex">
                  {selinaShortcut}
                </kbd>
              </span>
            </label>
          </form>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2.5">
            {showCommunity ? (
              <button
                type="button"
                data-tour="topbar-publish"
                onClick={handlePublish}
                aria-label={t("topbar.publish_aria")}
                className={cn(
                  "flex items-center gap-2 rounded-full bg-[#18181b] px-4 py-2 text-xs font-medium text-white shadow-sm transition-all duration-150 sm:px-5 sm:text-sm",
                  "hover:scale-[1.02] hover:bg-black active:scale-[0.98]",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground focus-visible:ring-offset-2",
                  "dark:bg-foreground dark:text-background dark:hover:bg-foreground/90"
                )}
              >
                <span className="hidden sm:inline">{t("topbar.publish")}</span>
                <SendHorizontal className="size-3.5 -rotate-[15deg]" aria-hidden />
              </button>
            ) : null}

            <button
              type="button"
              data-tour="topbar-search"
              onClick={() => setSearchOpen(true)}
              className={cn(
                "hidden items-center gap-1 rounded-full p-1.5 text-muted-foreground transition lg:flex",
                "hover:bg-muted/80 hover:text-foreground",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              )}
              aria-label={t("topbar.search_aria")}
              title={`${t("topbar.search_aria")} (${searchShortcut})`}
            >
              <Search className="size-4" aria-hidden />
              <span className="rounded-md border border-border/80 bg-muted px-1.5 py-0.5 text-[11px] font-medium text-muted-foreground shadow-sm">
                {searchShortcut}
              </span>
            </button>

            <button
              type="button"
              className={cn(
                "inline-flex size-9 items-center justify-center rounded-full text-muted-foreground transition lg:hidden",
                "hover:bg-muted/80 hover:text-foreground",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              )}
              onClick={() => setSearchOpen(true)}
              aria-label={t("topbar.search_aria")}
            >
              <Search className="size-4" aria-hidden />
            </button>

            <ResumeNotificationBell indicator="dot" />
          </div>
        </nav>
      </header>

      <GlobalSearchDialog open={searchOpen} onOpenChange={setSearchOpen} />
    </>
  );
}
