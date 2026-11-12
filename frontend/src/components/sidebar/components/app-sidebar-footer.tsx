import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";
import { truncateTitle } from "@/helpers/displayers/truncate-title";
import { Icons } from "@/lib/constants/icons";
import { useAuth } from "@/models/auth/hooks/useAuth";
import { useAuthSlice } from "@/models/auth/slice";
import { t } from "i18next";
import { ChevronUp } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function AppSidebarFooter() {
  const userFullName = useAuthSlice((state) => state.user?.full_name) ?? "Opps";
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

  const handleGoToMyAccount = () => {
    navigate("/my-account");
  };

  return (
    <SidebarMenu>
      <SidebarMenuItem className="flex items-center gap-0.5">
        <ModeToggle />
        <LanguageToggle />
      </SidebarMenuItem>

      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <div className="flex w-full items-center gap-2 rounded-md p-2 hover:bg-accent">
              <Icons.MyAccount className="h-4 w-4" />
              <p className="text-xs">{truncateTitle(userFullName, 18)}</p>
              <ChevronUp className="ml-auto" />
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            side="top"
            className="w-[--radix-popper-anchor-width]"
          >
            <DropdownMenuItem onClick={handleGoToMyAccount}>
              {t("sidebar.my_account")}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout}>
              {t("sidebar.disconnect")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
