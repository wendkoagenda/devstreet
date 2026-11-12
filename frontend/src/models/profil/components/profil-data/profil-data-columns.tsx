import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { GetProfilSchema } from "../../schema";

export const useProfilColumns = (): ColumnDef<GetProfilSchema>[] => {
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
      accessorKey: "is_company_owner",
      meta: { label: "Is company owner" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Is company owner
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const value = row.getValue("is_company_owner") as boolean | undefined;
        return <div>{value ? t("actions.yes") : t("actions.no")}</div>;
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
      accessorKey: "photo",
      meta: { label: "Photo" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Photo
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const path = row.getValue("photo") as string | null | undefined;
        if (!path) return <div>—</div>;
        const fileName = path.split("/").pop() ?? path;
        return (
          <a
            href={buildMediaUrl(path)}
            target="_blank"
            rel="noreferrer"
            className="text-primary underline truncate max-w-[200px] inline-block"
            title={fileName}
          >
            {fileName}
          </a>
        );
      },
    },
    {
      accessorKey: "headline",
      meta: { label: "Headline" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Headline
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("headline") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "bio",
      meta: { label: "Bio" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Bio
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("bio") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "phone",
      meta: { label: "Phone" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Phone
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("phone") ?? "—")}</div>;
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
      accessorKey: "remote",
      meta: { label: "Remote" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Remote
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const value = row.getValue("remote") as boolean | undefined;
        return <div>{value ? t("actions.yes") : t("actions.no")}</div>;
      },
    },
    {
      accessorKey: "timezone",
      meta: { label: "Timezone" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Timezone
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("timezone") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "default_hours_per_week",
      meta: { label: "Default hours per week" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Default hours per week
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("default_hours_per_week") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "is_open_to_work",
      meta: { label: "Is open to work" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Is open to work
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const value = row.getValue("is_open_to_work") as boolean | undefined;
        return <div>{value ? t("actions.yes") : t("actions.no")}</div>;
      },
    },
    {
      accessorKey: "daily_rate",
      meta: { label: "Daily rate" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Daily rate
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("daily_rate") ?? "—")}</div>;
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
      accessorKey: "years_of_experience",
      meta: { label: "Years of experience" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Years of experience
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("years_of_experience") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "languages",
      meta: { label: "Languages" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Languages
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("languages") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "github_url",
      meta: { label: "Github url" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Github url
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("github_url") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "linkedin_url",
      meta: { label: "Linkedin url" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Linkedin url
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("linkedin_url") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "portfolio_url",
      meta: { label: "Portfolio url" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Portfolio url
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("portfolio_url") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "cv_visibility",
      meta: { label: "Cv visibility" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Cv visibility
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"public": "Public", "companies": "Entreprises", "private": "Privé"} as Record<string, string>;
        const value = row.getValue("cv_visibility");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
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