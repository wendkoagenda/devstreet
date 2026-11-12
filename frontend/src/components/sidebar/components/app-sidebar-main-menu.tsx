import GeneralMenu from "./menu-groups/general-menu";
import UsersMenu from "./menu-groups/users-menu";

export default function AppSidebarMainMenu() {
  return (
    <>
      <GeneralMenu />
      <UsersMenu />
    </>
  );
}
