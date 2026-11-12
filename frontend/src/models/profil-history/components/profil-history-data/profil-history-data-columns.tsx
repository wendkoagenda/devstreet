import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GetProfilHistorySchema } from "../../schema";

export const useProfilHistoryColumns = (): ColumnDef<GetProfilHistorySchema>[] => {
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
      id: "profil",
      meta: { label: "Profil" },
      header: "Profil",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.profil, ["slug", "headline"])}</div>
      ),
    },
    {
      accessorKey: "field",
      meta: { label: "Field" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Field
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("field") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "old_value",
      meta: { label: "Old value" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Old value
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("old_value") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "new_value",
      meta: { label: "New value" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          New value
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("new_value") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "source",
      meta: { label: "Source" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Source
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"manual": "Saisie manuelle", "ai": "IA", "system": "Système"} as Record<string, string>;
        const value = row.getValue("source");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
  ];
};