import { relationLabel } from "@/helpers/api/relations";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { GetCandidatureSchema } from "../../schema";

export const useCandidatureColumns = (): ColumnDef<GetCandidatureSchema>[] => {
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
      id: "offer",
      meta: { label: "Offre" },
      header: "Offre",
      cell: ({ row }) => (
        <div>{relationLabel(row.original.offer, ["title"])}</div>
      ),
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
      accessorKey: "message",
      meta: { label: "Message" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Message
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("message") ?? "—")}</div>;
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
        const labels = {"sent": "Envoyée", "shortlisted": "Présélectionnée", "rejected": "Refusée", "accepted": "Acceptée"} as Record<string, string>;
        const value = row.getValue("status");
        return <div>{labels[String(value ?? "")] ?? String(value ?? "—")}</div>;
      },
    },
    {
      accessorKey: "ai_match_score",
      meta: { label: "Ai match score" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Ai match score
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("ai_match_score") ?? "—")}</div>;
      },
    },
    {
      accessorKey: "cv_snapshot",
      meta: { label: "Cv snapshot" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Cv snapshot
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const path = row.getValue("cv_snapshot") as string | null | undefined;
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
      accessorKey: "decided_at",
      meta: { label: "Decided at" },
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Decided at
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        return <div>{String(row.getValue("decided_at") ?? "—")}</div>;
      },
    },
  ];
};