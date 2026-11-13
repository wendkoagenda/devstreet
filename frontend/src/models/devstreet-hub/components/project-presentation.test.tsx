// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createInstance } from "i18next";
import { I18nextProvider } from "react-i18next";
import fr from "@/lib/locales/fr/common.json";
import { PresentationPanel } from "./project-presentation";
import type { Project } from "../schema";

const api = vi.hoisted(() => ({ save: vi.fn(), suggest: vi.fn(), consent: vi.fn(), fetch: vi.fn() }));
vi.mock("../api", () => ({
  useSavePresentationMutation: () => [api.save, { isLoading: false }],
  useSuggestPresentationMutation: () => [api.suggest],
  useSetAiConsentMutation: () => [api.consent, { isLoading: false }],
  useLazyGetAnalysisQuery: () => [api.fetch],
}));
vi.mock("sonner", () => ({ toast: { success: vi.fn() } }));

const project: Project = {
  id: 9, owner_id: 1, owner_display_name: "Aïcha Diallo", title: "Stock", slug: "stock",
  description: "Ma présentation initiale.", problem: "Un suivi plus simple.",
  declared_license: "MIT", status: "published", technologies: [], star_count: 0,
  images: [], ai_consent_at: "2026-11-13T10:00:00Z",
  repository: { id: 1, status: "ready", current_sha: "a".repeat(40) },
  created_at: "2026-11-13T10:00:00Z", updated_at: "2026-11-13T10:00:00Z",
};
const i18n = createInstance();
await i18n.init({ lng: "fr", fallbackLng: "fr", resources: { fr: { translation: fr } }, interpolation: { escapeValue: false } });

function show(overrides: Partial<Project> = {}, canEdit = true) {
  const navigate = vi.fn();
  render(<I18nextProvider i18n={i18n}><PresentationPanel project={{ ...project, ...overrides }} canEdit={canEdit} canAnalyze onNavigate={navigate} /></I18nextProvider>);
  return navigate;
}

beforeEach(() => {
  vi.clearAllMocks();
  api.save.mockImplementation(() => ({ unwrap: async () => project }));
  api.suggest.mockImplementation(() => ({ unwrap: async () => ({
    id: 8, status: "succeeded", project_id: project.id, commit_sha: "a".repeat(40),
    sources: [{ source_id: "src_01", path: "README.md" }],
    result: { description: "Une proposition améliorée.", references: [{ source_id: "src_01", line_start: 1, line_end: 2, reason: "README" }], unknowns: [] },
  }) }));
});
afterEach(cleanup);

describe("présentation libre et suggestion IA", () => {
  it("reste lisible sans image et sans sections prédéfinies", () => {
    const navigate = show({}, false);
    expect(screen.getByText(project.description)).toBeTruthy();
    expect(screen.queryByRole("img")).toBeNull();
    expect(screen.queryByRole("button", { name: "Modifier" })).toBeNull();
    expect(screen.queryByText("Ce que vous pouvez faire")).toBeNull();
    fireEvent.click(screen.getAllByRole("button", { name: "Voir les tâches" })[0]);
    expect(navigate).toHaveBeenCalledWith("contribute");
  });

  it("affiche du HTML utilisateur comme du texte inerte", () => {
    show({ description: '<script>alert("test")</script>' });
    expect(screen.getByText('<script>alert("test")</script>')).toBeTruthy();
    expect(document.querySelector("article script")).toBeNull();
  });

  it("ne remplace et n'enregistre jamais le texte à la génération", async () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: "Modifier" }));
    fireEvent.click(screen.getByRole("button", { name: "Améliorer la description avec l’IA" }));
    await screen.findByText("Une proposition améliorée.");
    const input = screen.getByLabelText("Présentation du projet") as HTMLTextAreaElement;
    expect(input.value).toBe(project.description);
    expect(api.save).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Utiliser cette proposition" }));
    expect(input.value).toBe("Une proposition améliorée.");
    expect(api.save).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer les modifications" }));
    await waitFor(() => expect(api.save).toHaveBeenCalledTimes(1));
    const body = api.save.mock.calls[0][0].body as FormData;
    expect(body.get("description")).toBe("Une proposition améliorée.");
    expect(body.get("base_updated_at")).toBe(project.updated_at);
    expect(body.getAll("images")).toHaveLength(0);
  });

  it("annuler conserve la présentation actuelle", () => {
    show();
    fireEvent.click(screen.getByRole("button", { name: "Modifier" }));
    fireEvent.change(screen.getByLabelText("Présentation du projet"), { target: { value: "Brouillon" } });
    fireEvent.click(screen.getByRole("button", { name: "Annuler" }));
    expect(screen.getByText(project.description)).toBeTruthy();
    expect(api.save).not.toHaveBeenCalled();
  });

  it("exige le consentement avant l'appel IA", () => {
    show({ ai_consent_at: null });
    fireEvent.click(screen.getByRole("button", { name: "Modifier" }));
    const button = screen.getByRole("button", { name: "Améliorer la description avec l’IA" }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    expect(api.suggest).not.toHaveBeenCalled();
  });

  it("une indisponibilité IA conserve le brouillon et permet la saisie manuelle", async () => {
    api.suggest.mockImplementation(() => ({ unwrap: async () => { throw { status: 503 }; } }));
    show();
    fireEvent.click(screen.getByRole("button", { name: "Modifier" }));
    fireEvent.click(screen.getByRole("button", { name: "Améliorer la description avec l’IA" }));
    await screen.findByRole("alert");
    expect((screen.getByLabelText("Présentation du projet") as HTMLTextAreaElement).value).toBe(project.description);
    expect((screen.getByRole("button", { name: "Enregistrer les modifications" }) as HTMLButtonElement).disabled).toBe(false);
    expect(api.save).not.toHaveBeenCalled();
  });
});
