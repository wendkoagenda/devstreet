import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { GetPrestationSchema } from "../../schema";

export const usePrestationColumns = (): ColumnDef<GetPrestationSchema>[] => {
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
      accessorKey: "category",
      meta: { label: "Category" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Category
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"web": "Web", "mobile": "Mobile", "design": "Design", "devops": "DevOps", "data": "Data", "other": "Autre"} as Record<string, string>;
        const value = row.getValue("category");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "price",
      meta: { label: "Price" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Price
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("price") ?? "—")}</div>;
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
      accessorKey: "delivery_days",
      meta: { label: "Delivery days" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Delivery days
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("delivery_days") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "revisions",
      meta: { label: "Revisions" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Revisions
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("revisions") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "cover_image",
      meta: { label: "Cover image" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Cover image
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const path = row.getValue("cover_image") as string | null | undefined;
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
      accessorKey: "is_active",
      meta: { label: "Is active" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Is active
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const value = row.getValue("is_active") as boolean | undefined;
        return <div>{value ? t("actions.yes") : t("actions.no")}</div>;
      },
    },
  ];
};