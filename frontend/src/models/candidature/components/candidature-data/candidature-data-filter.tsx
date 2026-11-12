import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import { Table } from "@tanstack/react-table";
import { GetCandidatureSchema } from "../../schema";
import { useCandidatureStore } from "../../slice";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useTranslation } from "react-i18next";
import { usePermissions } from "@/hooks/use-permissions";

export default function CandidatureDataFilter({
  table,
}: {
  table: Table<GetCandidatureSchema>;
}) {
  const { openCreateDialog } = useCandidatureStore();
  const { t } = useTranslation();
  const { canCreateCandidatures } = usePermissions();

  return (
    <div className="flex items-center justify-between py-4">
      <div className="flex gap-2">
        <Input
          placeholder={t("actions.filter")}
          value={table.getState().globalFilter ?? ""}
          onChange={(event) => {
            table.setGlobalFilter(event.target.value);
          }}
          className="max-w-sm"
        />
      </div>
      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="h-9 gap-2">
              {t("actions.columns")}
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => (
                <DropdownMenuCheckboxItem
                  key={column.id}
                  checked={column.getIsVisible()}
                  onCheckedChange={(value) => column.toggleVisibility(!!value)}
                >
                  {(column.columnDef.meta as { label?: string } | undefined)?.label ?? column.id}
                </DropdownMenuCheckboxItem>
              ))}
          </DropdownMenuContent>
        </DropdownMenu>

        { canCreateCandidatures && (
          <IconAndButtonDisplayer
            type="create"
            text={t("actions.create")}
            onClick={() => openCreateDialog()}
            style="none"
          />
        )}
      </div>
    </div>
  );
}