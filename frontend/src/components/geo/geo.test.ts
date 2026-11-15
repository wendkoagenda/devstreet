import { describe, expect, it } from "vitest";
import { COUNTRY_OPTIONS, countryName, filterCountries, findCountry, normalizeSearch } from "./countries";
import { hasFlag } from "./flags";
import { isValidOptionalPhone, splitPhone, toInternational } from "./phone";

describe("pays", () => {
  it("propose tous les pays, les pays suggérés en tête", () => {
    expect(COUNTRY_OPTIONS.length).toBeGreaterThan(200);
    expect(COUNTRY_OPTIONS[0]).toMatchObject({ code: "BJ", suggested: true });
    expect(COUNTRY_OPTIONS.findIndex((item) => !item.suggested)).toBe(18);
  });

  it("donne le nom en français et l'indicatif", () => {
    expect(findCountry("bf")).toMatchObject({ code: "BF", dialCode: "226" });
    expect(countryName("CI")).toMatch(/Ivoire/);
  });

  it("recherche sans accents, par code ou par indicatif", () => {
    expect(normalizeSearch("  Côte ")).toBe("cote");
    expect(filterCountries("cote").map((item) => item.code)).toContain("CI");
    expect(filterCountries("sn").map((item) => item.code)).toContain("SN");
    expect(filterCountries("+226").map((item) => item.code)).toContain("BF");
  });

  it("a un drapeau pour chaque pays suggéré", () => {
    for (const item of COUNTRY_OPTIONS.filter((country) => country.suggested)) {
      expect(hasFlag(item.code), item.code).toBe(true);
    }
  });
});

describe("téléphone", () => {
  it("enregistre le numéro au format international", () => {
    expect(toInternational("BF", "70 12 34 56")).toBe("+22670123456");
    expect(toInternational("FR", "06 12 34 56 78")).toBe("+33612345678");
    expect(toInternational("BF", "")).toBe("");
  });

  it("relit un numéro enregistré, ancien format compris", () => {
    expect(splitPhone("+22670123456", "FR")).toEqual({ country: "BF", national: "70 12 34 56" });
    expect(splitPhone("70123456", "BF").country).toBe("BF");
    expect(splitPhone("", "SN")).toEqual({ country: "SN", national: "" });
  });

  it("valide selon le pays, vide accepté", () => {
    expect(isValidOptionalPhone("")).toBe(true);
    expect(isValidOptionalPhone("+22670123456")).toBe(true);
    expect(isValidOptionalPhone("+2267012")).toBe(false);
    expect(isValidOptionalPhone("70123456")).toBe(false);
  });
});
