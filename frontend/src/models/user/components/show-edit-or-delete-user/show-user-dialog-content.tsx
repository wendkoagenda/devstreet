import { Label } from "@/components/ui/label";
import { Icons } from "@/lib/constants/icons";
import IconAndTextDisplayerAsTitle from "@/helpers/displayers/icon-and-text-displayer-as-title";
import { useTranslation } from "react-i18next";
import { useUserStore } from "../../slice";

export default function ShowUserDialogContent() {
  const { t } = useTranslation();
  const { selectedUser } = useUserStore();

  if (!selectedUser) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto pr-2">
        <div className="space-y-6">
          {/* Informations personnelles */}
          <div className="space-y-4">
            <IconAndTextDisplayerAsTitle
              Icon={Icons.User}
              text={t("personal_information")}
            />
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium">{t("first_name")}</Label>
                <p className="mt-1">{selectedUser.first_name}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">{t("last_name")}</Label>
                <p className="mt-1">{selectedUser.last_name}</p>
              </div>
            </div>
          </div>

          {/* Informations du compte */}
          <div className="space-y-4">
            <IconAndTextDisplayerAsTitle
              Icon={Icons.PersonalInformation}
              text={t("account_information")}
            />
            <div className="space-y-4">
              <div>
                <Label className="text-sm font-medium">{t("username")}</Label>
                <p className="mt-1">{selectedUser.username}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">{t("email")}</Label>
                <p className="mt-1">{selectedUser.email}</p>
              </div>
            </div>
          </div>

          {/* Rôles et permissions */}
          <div className="space-y-4">
            <IconAndTextDisplayerAsTitle
              Icon={Icons.Roles}
              text={t("roles_and_permissions")}
            />
            <div>
              <Label className="text-sm font-medium">{t("role_names")}</Label>
              <div className="mt-1 flex flex-wrap gap-2">
                {selectedUser.role_names &&
                selectedUser.role_names.length > 0 ? (
                  selectedUser.role_names.map((role) => (
                    <span
                      key={role}
                      className="px-2 py-1 bg-primary/10 text-primary rounded-md text-sm"
                    >
                      {role}
                    </span>
                  ))
                ) : (
                  <p className="text-muted-foreground">{t("no_roles")}</p>
                )}
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium">{t("is_active")}</Label>
              <p className="mt-1">
                {selectedUser.is_active ? t("yes") : t("no")}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
