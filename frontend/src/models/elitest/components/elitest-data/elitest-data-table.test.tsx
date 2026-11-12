// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  query: vi.fn(),
  response: {
    data: undefined as unknown,
    isLoading: false,
    isFetching: false,
    error: undefined as unknown,
  },
}));

vi.mock("../../api", () => ({
  useGetElitestsQuery: (params: unknown) => {
    mocks.query(params);
    return mocks.response;
  },
}));
vi.mock("./elitest-data-columns", () => ({
  useElitestColumns: () => [
    {
      accessorKey: "titre",
      header: ({ column }: { column: { toggleSorting: (desc?: boolean) => void; getIsSorted: () => false | "asc" | "desc" } }) => (
        <button
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          data-testid="sort-titre"
        >
          Titre
        </button>
      ),
      cell: ({ row }: { row: { original: { titre: string } } }) => row.original.titre,
    },
  ],
}));
vi.mock("./elitest-data-filter", () => ({
  default: ({ table }: { table: { getState: () => { globalFilter?: string }; setGlobalFilter: (v: string) => void } }) => (
    <input
      data-testid="search"
      value={table.getState().globalFilter ?? ""}
      onChange={(event) => table.setGlobalFilter(event.target.value)}
    />
  ),
}));
vi.mock("../../slice", () => ({
  useElitestStore: () => ({ setSelectedElitest: vi.fn(), openShowDialog: vi.fn() }),
}));
vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
vi.mock("@/helpers/loaders/table-loader", () => ({ default: () => <div data-testid="loader" /> }));

import { ElitestDataTableRender } from "./elitest-data-table";

const page = (count: number, titres: string[] = ["Alpha", "Beta"]) => ({
  count,
  next: null,
  previous: null,
  results: titres.map((titre, index) => ({ id: index + 1, titre })),
});

const lastParams = () => {
  const { calls } = mocks.query.mock;
  return calls[calls.length - 1]?.[0];
};

describe("tableau Elitest paginé côté serveur", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mocks.query.mockReset();
    mocks.response.data = page(45);
    mocks.response.isLoading = false;
    mocks.response.isFetching = false;
    mocks.response.error = undefined;
  });
  afterEach(() => {
    cleanup();
    vi.useRealTimers();
  });

  it("demande la première page au chargement", () => {
    render(<ElitestDataTableRender />);
    expect(lastParams()).toEqual({ page: 1, page_size: 20, search: undefined, ordering: undefined });
    expect(screen.getByText("Alpha")).toBeTruthy();
  });

  it("affiche un chargement avant la première réponse", () => {
    mocks.response.isLoading = true;
    render(<ElitestDataTableRender />);
    expect(screen.getByTestId("loader")).toBeTruthy();
  });

  it("n'affiche que la page reçue et le total du serveur", () => {
    render(<ElitestDataTableRender />);
    expect(screen.getByText(/0 pagination\.of 45/)).toBeTruthy();
    expect(screen.getByText(/1 \/ 3/)).toBeTruthy();
  });

  it("passe à la page suivante et revient en arrière", () => {
    render(<ElitestDataTableRender />);
    fireEvent.click(screen.getByText("pagination.next"));
    expect(lastParams().page).toBe(2);
    fireEvent.click(screen.getByText("pagination.previous"));
    expect(lastParams().page).toBe(1);
  });

  it("désactive Précédent sur la première page et Suivant sur la dernière", () => {
    mocks.response.data = page(5);
    render(<ElitestDataTableRender />);
    expect((screen.getByText("pagination.previous") as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByText("pagination.next") as HTMLButtonElement).disabled).toBe(true);
  });

  it("envoie la recherche au serveur après le délai, une seule fois", () => {
    render(<ElitestDataTableRender />);
    const input = screen.getByTestId("search");
    fireEvent.change(input, { target: { value: "caf" } });
    fireEvent.change(input, { target: { value: "café" } });
    expect(lastParams().search).toBeUndefined(); // pas encore : on attend la fin de la frappe
    act(() => vi.advanceTimersByTime(300));
    expect(lastParams().search).toBe("café");
  });

  it("repart de la première page quand la recherche change", () => {
    render(<ElitestDataTableRender />);
    fireEvent.click(screen.getByText("pagination.next"));
    expect(lastParams().page).toBe(2);
    fireEvent.change(screen.getByTestId("search"), { target: { value: "abc" } });
    act(() => vi.advanceTimersByTime(300));
    expect(lastParams()).toMatchObject({ page: 1, search: "abc" });
  });

  it("trie côté serveur : croissant puis décroissant", () => {
    render(<ElitestDataTableRender />);
    fireEvent.click(screen.getByTestId("sort-titre"));
    expect(lastParams().ordering).toBe("titre");
    fireEvent.click(screen.getByTestId("sort-titre"));
    expect(lastParams().ordering).toBe("-titre");
  });

  it("recule d'une page quand le serveur répond 404 (dernière page vidée)", () => {
    const { rerender } = render(<ElitestDataTableRender />);
    fireEvent.click(screen.getByText("pagination.next"));
    expect(lastParams().page).toBe(2);

    mocks.response.error = { status: 404, data: { detail: "Page invalide." } };
    rerender(<ElitestDataTableRender />);

    expect(lastParams().page).toBe(1);
  });

  it("ne recule pas sous la première page, même sur une 404", () => {
    mocks.response.error = { status: 404, data: { detail: "Page invalide." } };
    render(<ElitestDataTableRender />);
    expect(lastParams().page).toBe(1);
  });

  it("affiche « aucun résultat » quand la page est vide", () => {
    mocks.response.data = page(0, []);
    render(<ElitestDataTableRender />);
    expect(screen.getByText("no_results")).toBeTruthy();
  });
});
