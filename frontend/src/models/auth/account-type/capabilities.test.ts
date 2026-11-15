import { describe, expect, it } from "vitest";
import {
  ENTREPRISE_HOME_PATH,
  ONBOARDING_PATH,
  getAccessRedirect,
  getHomePath,
  isEntrepriseOnly,
  isPathAllowedForEntreprise,
  splitAccountType,
} from "./capabilities";

const entreprise = { account_type: "entreprise" as const, is_admin: false, onboarding_required: false };
const dev = { account_type: "dev" as const, is_admin: false, onboarding_required: false };
const both = { account_type: "both" as const, is_admin: false, onboarding_required: false };
const admin = { account_type: "" as const, is_admin: true, onboarding_required: false };
const fresh = { account_type: "" as const, is_admin: false, onboarding_required: true };

describe("splitAccountType", () => {
  it("décompose le type de compte en types simples", () => {
    expect(splitAccountType("both")).toEqual(["dev", "entreprise"]);
    expect(splitAccountType("dev")).toEqual(["dev"]);
    expect(splitAccountType("")).toEqual([]);
    expect(splitAccountType(undefined)).toEqual([]);
  });
});

describe("isEntrepriseOnly", () => {
  it("n'est vrai que pour le seul type entreprise, hors administrateur", () => {
    expect(isEntrepriseOnly(entreprise)).toBe(true);
    expect(isEntrepriseOnly(both)).toBe(false);
    expect(isEntrepriseOnly(dev)).toBe(false);
    expect(isEntrepriseOnly({ ...entreprise, is_admin: true })).toBe(false);
    expect(isEntrepriseOnly(null)).toBe(false);
  });
});

describe("isPathAllowedForEntreprise", () => {
  it.each([
    "/marketplace/offers",
    "/marketplace/my-offers/12",
    "/messages",
    "/messages/45",
    "/profil/me",
    "/profil/ada",
    "/my-account",
    "/entreprise/invitation/abc",
    "/forum/profil/3",
    "/forum/u/ada",
    "/hub/profiles/3",
    "/onboarding",
  ])("autorise %s", (path) => {
    expect(isPathAllowedForEntreprise(path)).toBe(true);
  });

  it.each([
    "/",
    "/forum/publications/4",
    "/forum/communautes",
    "/forum/chaines/2",
    "/forum/favoris",
    "/forum/invitation/code",
    "/hub/projects",
    "/hub/projects/12",
    "/users",
    "/roles",
    "/admin/marketplace",
  ])("refuse %s", (path) => {
    expect(isPathAllowedForEntreprise(path)).toBe(false);
  });

  it("ne confond pas un préfixe avec un autre chemin qui commence pareil", () => {
    expect(isPathAllowedForEntreprise("/marketplaceX")).toBe(false);
    expect(isPathAllowedForEntreprise("/messagesfoo")).toBe(false);
  });
});

describe("getHomePath", () => {
  it("envoie l'entreprise seule sur la marketplace et les autres sur le fil", () => {
    expect(getHomePath(entreprise)).toBe(ENTREPRISE_HOME_PATH);
    expect(getHomePath(dev)).toBe("/");
    expect(getHomePath(both)).toBe("/");
    expect(getHomePath(admin)).toBe("/");
  });
});

describe("getAccessRedirect", () => {
  it("ne redirige pas sans utilisateur", () => {
    expect(getAccessRedirect(null, "/hub/projects")).toBeNull();
  });

  it("impose le choix du type tant qu'il n'est pas fait", () => {
    expect(getAccessRedirect(fresh, "/")).toBe(ONBOARDING_PATH);
    expect(getAccessRedirect(fresh, "/marketplace/offers")).toBe(ONBOARDING_PATH);
    expect(getAccessRedirect(fresh, ONBOARDING_PATH)).toBeNull();
  });

  it("renvoie l'entreprise seule vers la marketplace hors de ses pages autorisées", () => {
    expect(getAccessRedirect(entreprise, "/")).toBe(ENTREPRISE_HOME_PATH);
    expect(getAccessRedirect(entreprise, "/hub/projects/3")).toBe(ENTREPRISE_HOME_PATH);
    expect(getAccessRedirect(entreprise, "/forum/communautes")).toBe(ENTREPRISE_HOME_PATH);
    expect(getAccessRedirect(entreprise, "/messages/3")).toBeNull();
    expect(getAccessRedirect(entreprise, "/profil/me")).toBeNull();
  });

  it("laisse les comptes dev, les deux et administrateur circuler librement", () => {
    for (const user of [dev, both, admin]) {
      expect(getAccessRedirect(user, "/")).toBeNull();
      expect(getAccessRedirect(user, "/hub/projects")).toBeNull();
    }
  });
});
