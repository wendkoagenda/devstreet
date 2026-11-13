import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";
import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { Icons } from "@/lib/constants/icons";
import { useTranslation } from "react-i18next";
import ChangePasswordDialog from "../components/change-password/change-password-dialog";
import { ProfilePhotoCard } from "../components/profile-photo-card";
import { useChangePasswordDialogStore } from "../slice";
import { useEffect, useState } from "react";

import { MyAccountLoader } from "../../../helpers/loaders/my-account-loader";
import type { User } from "../schema";
import { useAuthSlice } from "../slice";
import { MyAccountHubProfile } from "@/models/devstreet-hub/components/my-account-hub-profile";
import { ConnectedComputersSection } from "@/models/devstreet-hub/components/connected-computers-section";

export default function MyAccount() {
  const { t } = useTranslation();
  const { openChangePasswordDialog } = useChangePasswordDialogStore();
  const sessionUser = useAuthSlice((state) => state.user);

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionUser) {
      setUser(sessionUser);
      setError(null);
      setIsLoading(false);
      return;
    }

    const fetchUser = () => {
      try {
        const userData = localStorage.getItem("user");
        if (userData) {
          const parsedUser = JSON.parse(userData) as User;
          setUser(parsedUser);
        } else {
          setError("No user data found");
        }
      } catch (error) {
        console.error("Error parsing user data", error);
        setError("Invalid user data format");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [sessionUser]);

  if (isLoading) {
    return <MyAccountLoader />;
  }

  if (error || !user) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Icons.Security className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  {t("my_account.error_title", "Unable to load account")}
                </h3>
                <p className="text-muted-foreground">
                  {error ||
                    t("my_account.no_user_data", "No user data available")}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <PageTitleDisplayer
        title={t("my_account.title")}
        description={t("my_account.description")}
      />
      <div className="mb-6">
        <ProfilePhotoCard user={user} onUserUpdated={setUser} />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Informations personnelles */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Icons.PersonalInformation className="h-5 w-5" />
            <h2 className="text-lg font-semibold">
              {t("my_account.personal_info")}
            </h2>
          </CardHeader>
          <CardContent>
            <Table>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">
                    {t("my_account.full_name")}
                  </TableCell>
                  <TableCell>{user.full_name || "—"}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">
                    {t("my_account.username")}
                  </TableCell>
                  <TableCell>{user.username || "—"}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">
                    {t("my_account.email")}
                  </TableCell>
                  <TableCell>{user.email || "—"}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Rôles et permissions */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Icons.Roles className="h-5 w-5" />
            <h2 className="text-lg font-semibold">
              {t("my_account.roles_and_permissions")}
            </h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Section Rôles */}
              <div>
                <h3 className="font-medium mb-2">{t("my_account.roles")}</h3>
                <div className="flex flex-wrap gap-2">
                  {user.roles && user.roles.length > 0 ? (
                    user.roles.map((role: string) => (
                      <span
                        key={role}
                        className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm"
                      >
                        {role}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      {t("my_account.no_roles", "No roles assigned")}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sécurité */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Icons.Security className="h-5 w-5" />
            <h2 className="text-lg font-semibold">
              {t("my_account.security")}
            </h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">{t("my_account.password")}</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {t("my_account.password_description")}
                </p>
                <Button onClick={openChangePasswordDialog}>
                  <Icons.Security className="mr-2 h-4 w-4" />
                  {t("change_password.button")}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <ConnectedComputersSection />

      {user.id ? <MyAccountHubProfile userId={user.id} /> : null}

      <ChangePasswordDialog />
    </div>
  );
}
