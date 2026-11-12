// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const refresh = vi.hoisted(() => ({ refreshSession: vi.fn() }));
vi.mock("@/helpers/api/base-query", () => refresh);
vi.mock("@/helpers/api/csrf", () => ({
  API_URL: "/api",
  resetCsrfToken: vi.fn(),
}));

import { fetchSession } from "./session-api";

const SESSION = {
  user: { id: 1, full_name: "Ada", username: "ada", email: "ada@example.com" },
  permissions: ["users.view"],
};

const json = (status: number, body: unknown = {}) =>
  new Response(JSON.stringify(body), { status });

describe("fetchSession : absence de session et pannes sont distinguées", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    refresh.refreshSession.mockReset().mockResolvedValue(false);
    vi.stubGlobal("fetch", fetchMock);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("retourne la session quand le serveur répond 200", async () => {
    fetchMock.mockResolvedValue(json(200, SESSION));
    expect(await fetchSession()).toEqual(SESSION);
  });

  it("retourne null quand il n'y a pas de session (401 puis renouvellement refusé)", async () => {
    fetchMock.mockResolvedValue(json(401));
    expect(await fetchSession()).toBeNull();
  });

  it("relit la session après un renouvellement réussi", async () => {
    refresh.refreshSession.mockResolvedValue(true);
    fetchMock.mockResolvedValueOnce(json(401)).mockResolvedValueOnce(json(200, SESSION));
    expect(await fetchSession()).toEqual(SESSION);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("LÈVE sur une erreur serveur au lieu de la faire passer pour une absence de session", async () => {
    fetchMock.mockResolvedValue(json(500));
    await expect(fetchSession()).rejects.toThrow("HTTP 500");
  });

  it("LÈVE quand le serveur est injoignable", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(fetchSession()).rejects.toThrow("Failed to fetch");
  });

  it("LÈVE quand le renouvellement échoue sur une panne réseau", async () => {
    fetchMock.mockResolvedValue(json(401));
    refresh.refreshSession.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(fetchSession()).rejects.toThrow("Failed to fetch");
  });
});
