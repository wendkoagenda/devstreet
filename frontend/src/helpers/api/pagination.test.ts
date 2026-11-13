import { describe, expect, it } from "vitest";
import {
  PAGE_SIZE,
  cursorFromUrl,
  orderingOf,
  pageCountOf,
  toQueryString,
} from "./pagination";

describe("toQueryString", () => {
  it("retourne une chaîne vide sans paramètre", () => {
    expect(toQueryString()).toBe("");
    expect(toQueryString(undefined)).toBe("");
    expect(toQueryString({})).toBe("");
  });

  it("construit la requête avec les paramètres renseignés", () => {
    expect(toQueryString({ page: 2, page_size: 20 })).toBe("?page=2&page_size=20");
    expect(toQueryString({ search: "café", ordering: "-prix" })).toBe("?search=caf%C3%A9&ordering=-prix");
  });

  it("ignore les paramètres vides ou absents", () => {
    expect(toQueryString({ page: 1, search: "", ordering: undefined })).toBe("?page=1");
  });

  it("garde la page 0 ou une valeur numérique nulle (seuls vide et absent sont ignorés)", () => {
    expect(toQueryString({ page: 0 })).toBe("?page=0");
  });

  it("encode les caractères qui casseraient la requête", () => {
    expect(toQueryString({ search: "a&b=c d" })).toBe("?search=a%26b%3Dc+d");
  });
});

describe("pageCountOf", () => {
  it("arrondit au supérieur", () => {
    expect(pageCountOf(41, 20)).toBe(3);
    expect(pageCountOf(40, 20)).toBe(2);
    expect(pageCountOf(1, 20)).toBe(1);
  });

  it("garde au moins une page, même sans résultat", () => {
    expect(pageCountOf(0)).toBe(1);
  });

  it("utilise la taille de page par défaut", () => {
    expect(PAGE_SIZE).toBe(20);
    expect(pageCountOf(PAGE_SIZE + 1)).toBe(2);
  });
});

describe("cursorFromUrl", () => {
  it("retourne undefined sans URL", () => {
    expect(cursorFromUrl(null)).toBeUndefined();
    expect(cursorFromUrl(undefined)).toBeUndefined();
    expect(cursorFromUrl("")).toBeUndefined();
  });

  it("extrait le curseur d'une URL absolue", () => {
    expect(
      cursorFromUrl("http://127.0.0.1:8000/api/v1/publications?cursor=abc%3D&page_size=20")
    ).toBe("abc=");
  });

  it("extrait le curseur d'une URL relative", () => {
    expect(cursorFromUrl("/api/v1/publications?cursor=xyz")).toBe("xyz");
  });
});

describe("orderingOf", () => {
  it("n'envoie pas de tri quand rien n'est trié", () => {
    expect(orderingOf([])).toBeUndefined();
  });

  it("préfixe par - pour un tri décroissant", () => {
    expect(orderingOf([{ id: "prix", desc: false }])).toBe("prix");
    expect(orderingOf([{ id: "prix", desc: true }])).toBe("-prix");
  });

  it("ne retient que le premier tri (le serveur n'en gère qu'un)", () => {
    expect(orderingOf([{ id: "titre", desc: false }, { id: "prix", desc: true }])).toBe("titre");
  });
});
