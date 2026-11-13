import GeneralMenu from "./menu-groups/general-menu";
import PlatformMenu from "./menu-groups/platform-menu";
import UsersMenu from "./menu-groups/users-menu";

export default function AppSidebarMainMenu() {
  return (
    <div className="flex flex-col gap-2.5">
      <PlatformMenu />
      <GeneralMenu />
      <UsersMenu />
    </div>
  );
}
