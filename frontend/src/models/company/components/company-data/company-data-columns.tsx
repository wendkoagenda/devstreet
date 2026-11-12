import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { GetCompanySchema } from "../../schema";

export const useCompanyColumns = (): ColumnDef<GetCompanySchema>[] => {
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
      accessorKey: "name",
      meta: { label: "Name" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("name") ?? "—")}</div>;
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
      accessorKey: "logo",
      meta: { label: "Logo" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Logo
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const path = row.getValue("logo") as string | null | undefined;
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
      accessorKey: "sector",
      meta: { label: "Sector" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Sector
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"fintech": "Fintech", "ecommerce": "E-commerce", "agritech": "Agritech", "edtech": "Edtech", "health": "Santé", "ngo": "ONG", "public": "Secteur public", "other": "Autre"} as Record<string, string>;
        const value = row.getValue("sector");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "size",
      meta: { label: "Size" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Size
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const labels = {"1-10": "1-10", "11-50": "11-50", "51-200": "51-200", "200+": "200+"} as Record<string, string>;
        const value = row.getValue("size");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "website",
      meta: { label: "Website" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Website
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("website") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "contact_email",
      meta: { label: "Contact email" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Contact email
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("contact_email") ?? "—")}</div>;
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
      accessorKey: "address",
      meta: { label: "Address" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Address
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("address") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "is_verified",
      meta: { label: "Is verified" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Is verified
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const value = row.getValue("is_verified") as boolean | undefined;
        return <div>{value ? t("actions.yes") : t("actions.no")}</div>;
      },
    },
    {
      accessorKey: "verified_at",
      meta: { label: "Verified at" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Verified at
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("verified_at") ?? "—")}</div>;
      },
    },
  ];
};