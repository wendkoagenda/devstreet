import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GetReviewSchema } from "../../schema";

export const useReviewColumns = (): ColumnDef<GetReviewSchema>[] => {
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
      id: "target",
      meta: { label: "Profil noté" },
      header: "Profil noté",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.target, ["slug", "headline"])}</div>
      ),
    },
    {
      id: "author",
      meta: { label: "Auteur de l'avis" },
      header: "Auteur de l'avis",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.author, ["slug", "headline"])}</div>
      ),
    },
    {
      id: "candidature",
      meta: { label: "Candidature" },
      header: "Candidature",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.candidature, [])}</div>
      ),
    },
    {
      accessorKey: "rating",
      meta: { label: "Rating" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Rating
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("rating") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "comment",
      meta: { label: "Comment" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Comment
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("comment") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "is_public",
      meta: { label: "Is public" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Is public
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const value = row.getValue("is_public") as boolean | undefined;
        return <div>{value ? t("actions.yes") : t("actions.no")}</div>;
      },
    },
  ];
};