import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GetSwipeSchema } from "../../schema";

export const useSwipeColumns = (): ColumnDef<GetSwipeSchema>[] => {
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
      id: "author",
      meta: { label: "Auteur du swipe" },
      header: "Auteur du swipe",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.author, ["slug", "headline"])}</div>
      ),
    },
    {
      id: "target",
      meta: { label: "Profil ciblé" },
      header: "Profil ciblé",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.target, ["slug", "headline"])}</div>
      ),
    },
    {
      accessorKey: "direction",
      meta: { label: "Direction" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Direction
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"like": "Like", "pass": "Passer"} as Record<string, string>;
        const value = row.getValue("direction");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "context",
      meta: { label: "Context" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Context
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"recruit": "Recrutement", "network": "Réseau"} as Record<string, string>;
        const value = row.getValue("context");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
  ];
};