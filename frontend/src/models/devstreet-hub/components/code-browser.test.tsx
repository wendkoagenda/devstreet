// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { CodeBrowser } from "./code-browser";

const state = vi.hoisted(() => ({ current: {} as Record<string, unknown> }));
vi.mock("../hooks/use-project-code", () => ({ useProjectCode: () => state.current }));
vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));
afterEach(cleanup);

function show(patch: Record<string, unknown> = {}) {
  state.current = {
    summary: undefined, branches: [], tree: undefined, blob: undefined,
    isEmpty: false, isLoading: false, isFetching: false, isError: false,
    metadataError: false, ref: "main", path: "", mode: "tree",
    breadcrumbs: [{ label: "", path: "" }], ...patch,
  };
  render(<CodeBrowser projectId={5} projectTitle="Stock" isOwner={false} namespaceHint="user" repoNameHint="stock" />);
}

const tree = { entries: [{ name: "index.html", path: "index.html", type: "file", size: 64 }], latest_commit: null, readme: null };

describe("chargement progressif du dépôt", () => {
  it("affiche un skeleton accessible au premier chargement", () => {
    show({ isLoading: true, isFetching: true });
    expect(screen.getByRole("status").getAttribute("aria-busy")).toBe("true");
    expect(screen.queryByText("hub.detail.code.folder_empty")).toBeNull();
  });

  it("affiche les fichiers sans attendre les statistiques", () => {
    show({ tree, isFetching: true });
    expect(screen.getByText("index.html")).toBeTruthy();
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("une panne des statistiques ne masque pas les fichiers", () => {
    show({ tree, metadataError: true });
    expect(screen.getByText("index.html")).toBeTruthy();
    expect(screen.getByRole("status").textContent).toBe("hub.detail.code.metadata_unavailable");
  });

  it("ne présente pas un dossier en chargement comme vide", () => {
    show({ summary: { stats: {}, languages: [] }, isLoading: true, isFetching: true });
    expect(screen.getByRole("status").getAttribute("aria-busy")).toBe("true");
    expect(screen.queryByText("hub.detail.code.folder_empty")).toBeNull();
  });
});
