import {
  flexRender,
  getCoreRowModel,
  PaginationState,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useEffect, useState } from "react";
import { useGetProfilHistoriesQuery } from "../../api";
import { useProfilHistoryColumns } from "./profil-history-data-columns";
import ProfilHistoryDataFilter from "./profil-history-data-filter";
import { useTranslation } from "react-i18next";
import { useProfilHistoryStore } from "../../slice";
import TableLoader from "@/helpers/loaders/table-loader";
import { PAGE_SIZE, orderingOf, pageCountOf } from "@/helpers/api/pagination";
import { useDebouncedValue } from "@/hooks/use-debounced-value";

export function ProfilHistoryDataTableRender() {
  const { setSelectedProfilHistory, openShowDialog } = useProfilHistoryStore();
  const columns = useProfilHistoryColumns();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: PAGE_SIZE,
  });
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});
  const { t } = useTranslation();

  // La recherche, le tri et la pagination sont faits par le serveur : une requête par page demandée
  const search = useDebouncedValue(globalFilter, 300);
  const { data, isLoading, isFetching, error } = useGetProfilHistoriesQuery({
    page: pagination.pageIndex + 1,
    page_size: pagination.pageSize,
    search: search || undefined,
    ordering: orderingOf(sorting),
  });

  // Une nouvelle recherche ou un nouveau tri repart de la première page, sans sélection
  useEffect(() => {
    setPagination((current) =>
      current.pageIndex === 0 ? current : { ...current, pageIndex: 0 }
    );
    setRowSelection({});
  }, [search, sorting]);

  // Changer de page efface la sélection (les lignes sélectionnées appartenaient à l'ancienne page)
  useEffect(() => {
    setRowSelection({});
  }, [pagination.pageIndex]);

  // Dernière page vidée (suppression du dernier élément) : le serveur répond 404, on recule d'une page
  const notFoundPage =
    error !== undefined && "status" in error && error.status === 404;
  useEffect(() => {
    if (notFoundPage) {
      setPagination((current) =>
        current.pageIndex > 0 ? { ...current, pageIndex: current.pageIndex - 1 } : current
      );
    }
  }, [notFoundPage]);

  const total = data?.count ?? 0;

  const table = useReactTable({
    data: data?.results ?? [],
    columns,
    manualPagination: true,
    manualSorting: true,
    manualFiltering: true,
    pageCount: pageCountOf(total, pagination.pageSize),
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      pagination,
      globalFilter,
      columnVisibility,
      rowSelection,
    },
  });

  if (isLoading) return <TableLoader />;

  return (
    <div className="w-full">
      <ProfilHistoryDataFilter table={table} />
      <div className={`overflow-hidden rounded-md border transition-opacity ${isFetching ? "opacity-60" : ""}`}>
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell
                      key={cell.id}
                      onClick={() => {
                        if (cell.column.id !== "select") {
                          setSelectedProfilHistory(row.original);
                          openShowDialog();
                        }
                      }}
                      className={cell.column.id !== "select" ? "cursor-pointer" : ""}
                    >
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  {t("no_results")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="text-muted-foreground flex-1 text-sm">
          {table.getSelectedRowModel().rows.length} {t("pagination.of")} {total}{" "}
          {t("actions.selected")} · {pagination.pageIndex + 1} / {table.getPageCount()}
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            {t("pagination.previous")}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            {t("pagination.next")}
          </Button>
        </div>
      </div>
    </div>
  );
}