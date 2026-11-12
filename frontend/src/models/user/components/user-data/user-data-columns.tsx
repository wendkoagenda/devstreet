import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { GetUserSchema } from "../../schema";
import { useTranslation } from "react-i18next";

export const useUserColumns = (): ColumnDef<GetUserSchema>[] => {
  const { t } = useTranslation();

  return [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && "indeterminate")
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label={t("actions.select_all")}
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label={t("actions.select_row")}
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: "is_active",
      meta: { label: t("users.status") },
      header: t("users.status"),
      cell: ({ row }) => (
        <div className="capitalize">
          {row.getValue("is_active") ? t("users.active") : t("users.inactive")}
        </div>
      ),
    },
    {
      accessorKey: "username",
      meta: { label: t("users.username") },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {t("users.username")}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <div className="lowercase">{row.getValue("username")}</div>
      ),
    },
    {
      accessorKey: "first_name",
      meta: { label: t("users.first_name") },
      header: () => <div className="text-right">{t("users.first_name")}</div>,
      cell: ({ row }) => {
        const first_name = row.getValue("first_name") as string;
        return <div className="text-right font-medium">{first_name}</div>;
      },
    },
    {
      accessorKey: "last_name",
      meta: { label: t("users.last_name") },
      header: () => <div className="text-right">{t("users.last_name")}</div>,
      cell: ({ row }) => (
        <div className="text-right font-medium">
          {row.getValue("last_name")}
        </div>
      ),
    },
    {
      accessorKey: "email",
      meta: { label: t("users.email") },
      header: () => <div className="text-right">{t("users.email")}</div>,
      cell: ({ row }) => (
        <div className="text-right font-medium">{row.getValue("email")}</div>
      ),
    },
    {
      accessorKey: "roles",
      meta: { label: t("users.roles") },
      header: () => <div className="text-right">{t("users.roles")}</div>,
      cell: ({ row }) => {
        const roles = row.getValue("roles") as { id: number; name: string }[];

        return (
          <div className="text-right font-medium">
            {roles && roles.length > 0
              ? roles.map((role) => role.name).join(", ")
              : "—"}
          </div>
        );
      },
    },
  ];
};
