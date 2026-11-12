import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GetOfferSchema } from "../../schema";

export const useOfferColumns = (): ColumnDef<GetOfferSchema>[] => {
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
      id: "company",
      meta: { label: "Entreprise" },
      header: "Entreprise",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.company, ["name"])}</div>
      ),
    },
    {
      id: "recruiter",
      meta: { label: "Recruteur" },
      header: "Recruteur",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.recruiter, ["slug", "headline"])}</div>
      ),
    },
    {
      accessorKey: "title",
      meta: { label: "Title" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Title
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("title") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "slug",
      meta: { label: "Slug" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Slug
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("slug") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "description",
      meta: { label: "Description" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Description
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("description") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "type",
      meta: { label: "Type" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Type
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"mission": "Mission", "cdd": "CDD", "cdi": "CDI", "stage": "Stage"} as Record<string, string>;
        const value = row.getValue("type");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "contract_duration",
      meta: { label: "Contract duration" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Contract duration
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("contract_duration") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "experience_level",
      meta: { label: "Experience level" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Experience level
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"junior": "Junior", "mid": "Confirmé", "senior": "Sénior"} as Record<string, string>;
        const value = row.getValue("experience_level");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "budget_min",
      meta: { label: "Budget min" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Budget min
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("budget_min") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "budget_max",
      meta: { label: "Budget max" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Budget max
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("budget_max") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "currency",
      meta: { label: "Currency" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Currency
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("currency") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "budget_period",
      meta: { label: "Budget period" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Budget period
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"day": "Par jour", "month": "Par mois", "fixed": "Forfait"} as Record<string, string>;
        const value = row.getValue("budget_period");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "country",
      meta: { label: "Country" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Country
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("country") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "city",
      meta: { label: "City" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          City
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("city") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "work_mode",
      meta: { label: "Work mode" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Work mode
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"on_site": "Sur site", "hybrid": "Hybride", "remote": "À distance"} as Record<string, string>;
        const value = row.getValue("work_mode");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
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
      accessorKey: "deadline",
      meta: { label: "Deadline" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Deadline
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("deadline") ?? "—")}</div>;
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
        const labels = {"draft": "Brouillon", "open": "Ouverte", "closed": "Clôturée"} as Record<string, string>;
        const value = row.getValue("status");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "published_at",
      meta: { label: "Published at" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Published at
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("published_at") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "views_count",
      meta: { label: "Views count" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Views count
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("views_count") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "embedding",
      meta: { label: "Embedding" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Embedding
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("embedding") ?? "—")}</div>;
      },
    },
  ];
};