import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GetAvailabilitySchema } from "../../schema";

export const useAvailabilityColumns = (): ColumnDef<GetAvailabilitySchema>[] => {
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
      accessorKey: "start_date",
      meta: { label: "Start date" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Start date
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("start_date") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "end_date",
      meta: { label: "End date" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          End date
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("end_date") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "status",
      meta: { label: "Status" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Status
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"available": "Disponible", "partial": "Partiel", "busy": "Occupé", "leave": "Congé"} as Record<string, string>;
        const value = row.getValue("status");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "hours_per_week",
      meta: { label: "Hours per week" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Hours per week
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("hours_per_week") ?? "—")}</div>;
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
        const labels = {"manual": "Saisie manuelle", "mission": "Mission"} as Record<string, string>;
        const value = row.getValue("source");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "note",
      meta: { label: "Note" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Note
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("note") ?? "—")}</div>;
      },
    },
  ];
};