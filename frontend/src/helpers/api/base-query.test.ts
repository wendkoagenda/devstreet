// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SESSION_EXPIRED_EVENT, baseQuery, authBaseQuery } from "./base-query";

const json = (status: number, body: unknown = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

const apiStub = (type: "query" | "mutation" = "query") =>
  ({
    signal: new AbortController().signal,
    dispatch: vi.fn(),
    getState: vi.fn(),
    extra: undefined,
    endpoint: "test",
    type,
    forced: false,
  }) as never;

const urlOf = (call: unknown[]) =>
  typeof call[0] === "string" ? call[0] : (call[0] as Request).url;

describe("requêtes API par cookies", () => {
  const fetchMock = vi.fn();
  const expired = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    expired.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    window.addEventListener(SESSION_EXPIRED_EVENT, expired);
    document.cookie = "csrftoken=jeton-csrf";
  });
  afterEach(() => {
    window.removeEventListener(SESSION_EXPIRED_EVENT, expired);
    document.cookie = "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    vi.unstubAllGlobals();
  });

  it("envoie les cookies avec chaque requête, sans en-tête Authorization", async () => {
    fetchMock.mockResolvedValue(json(200, [1]));
    await baseQuery("/users", apiStub(), {});

    const request = fetchMock.mock.calls[0][0] as Request;
    expect(request.credentials).toBe("include");
    expect(request.headers.get("Authorization")).toBeNull();
    expect(request.headers.get("X-CSRFToken")).toBeNull(); // lecture : pas de CSRF
  });

  it("ajoute le jeton CSRF aux requêtes modifiantes", async () => {
    fetchMock.mockResolvedValue(json(200));
    await baseQuery({ url: "/users", method: "POST", body: {} }, apiStub("mutation"), {});

    expect((fetchMock.mock.calls[0][0] as Request).headers.get("X-CSRFToken")).toBe("jeton-csrf");
  });

  it("demande le jeton au serveur quand le cookie n'est pas lisible", async () => {
    document.cookie = "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    fetchMock.mockImplementation(async (input: Request | string) => {
      const url = typeof input === "string" ? input : input.url;
      return url.endsWith("/auth/csrf") ? json(200, { csrfToken: "depuis-le-serveur" }) : json(200);
    });

    await baseQuery({ url: "/users", method: "POST", body: {} }, apiStub("mutation"), {});

    const sent = fetchMock.mock.calls.find((c) => urlOf(c).endsWith("/users"))![0] as Request;
    expect(sent.headers.get("X-CSRFToken")).toBe("depuis-le-serveur");
  });

  it("sur 401 renouvelle la session puis rejoue la requête", async () => {
    fetchMock
      .mockResolvedValueOnce(json(401))
      .mockResolvedValueOnce(json(200)) // /auth/token/refresh
      .mockResolvedValueOnce(json(200, ["ok"]));

    const result = await baseQuery("/users", apiStub(), {});

    expect(result.data).toEqual(["ok"]);
    expect(fetchMock.mock.calls[1][0]).toMatch(/\/auth\/token\/refresh$/);
    expect(expired).not.toHaveBeenCalled();
  });

  it("termine la session quand le renouvellement échoue", async () => {
    fetchMock.mockResolvedValueOnce(json(401)).mockResolvedValueOnce(json(401));

    const result = await baseQuery("/users", apiStub(), {});

    expect(result.error?.status).toBe(401);
    expect(expired).toHaveBeenCalledTimes(1);
  });

  it("garde la session quand le serveur est injoignable pendant le renouvellement", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    fetchMock
      .mockResolvedValueOnce(json(401))
      .mockRejectedValueOnce(new TypeError("Failed to fetch")); // /auth/token/refresh

    const result = await baseQuery("/users", apiStub(), {});

    expect(result.error?.status).toBe(401); // l'erreur d'origine est conservée
    expect(expired).not.toHaveBeenCalled(); // la session n'est pas déclarée terminée
    consoleError.mockRestore();
  });

  it("partage un seul renouvellement entre plusieurs requêtes en 401", async () => {
    let refreshCalls = 0;
    fetchMock.mockImplementation(async (input: Request | string) => {
      const url = typeof input === "string" ? input : input.url;
      if (url.endsWith("/auth/token/refresh")) {
        refreshCalls += 1;
        return json(200);
      }
      // 401 au premier passage de chaque requête, 200 au rejeu
      const seen = fetchMock.mock.calls.filter((c) => urlOf(c) === url).length;
      return seen <= 1 ? json(401) : json(200, []);
    });

    await Promise.all([
      baseQuery("/users", apiStub(), {}),
      baseQuery("/roles", apiStub(), {}),
      baseQuery("/elitests", apiStub(), {}),
    ]);

    expect(refreshCalls).toBe(1);
  });

  it("ne tente pas de renouvellement sur les routes publiques (mauvais identifiants)", async () => {
    fetchMock.mockResolvedValue(json(401, { detail: "Identifiants invalides" }));

    const result = await authBaseQuery(
      { url: "/auth/login", method: "POST", body: {} },
      apiStub("mutation"),
      {}
    );

    expect(result.error?.status).toBe(401);
    expect(fetchMock.mock.calls.some((c) => urlOf(c).endsWith("/auth/token/refresh"))).toBe(false);
    expect(expired).not.toHaveBeenCalled();
  });
});
