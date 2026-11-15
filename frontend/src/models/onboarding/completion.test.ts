import { describe, expect, it } from "vitest";
import type { MyCompany, MyProfil } from "@/models/marketplace-space/schema";
import { buildCompletionItems, completionPercent } from "./completion";

const profil = { bio: "", github_url: "", linkedin_url: "", portfolio_url: "" } as MyProfil;
const company = { description: "", contact_email: "", website: "" } as MyCompany;

describe("buildCompletionItems", () => {
  it("ne propose que les éléments des types du compte", () => {
    const devOnly = buildCompletionItems({
      wantsDev: true,
      wantsEntreprise: false,
      profil: null,
      company: null,
      skillsCount: 0,
    });
    expect(devOnly.every((item) => item.id.startsWith("dev-"))).toBe(true);

    const entrepriseOnly = buildCompletionItems({
      wantsDev: false,
      wantsEntreprise: true,
      profil: null,
      company: null,
      skillsCount: 0,
    });
    expect(entrepriseOnly.every((item) => item.id.startsWith("company-"))).toBe(true);
  });

  it("marque comme faits les éléments renseignés", () => {
    const items = buildCompletionItems({
      wantsDev: true,
      wantsEntreprise: true,
      profil: { ...profil, bio: "Dev", github_url: "https://github.com/ada" },
      company: { ...company, description: "Studio" },
      skillsCount: 2,
    });
    const done = Object.fromEntries(items.map((item) => [item.id, item.done]));
    expect(done).toMatchObject({
      "dev-profil": true,
      "dev-skills": true,
      "dev-bio": true,
      "dev-links": true,
      "company-created": true,
      "company-description": true,
      "company-contact": false,
    });
  });
});

describe("completionPercent", () => {
  it("vaut 0 sans élément", () => {
    expect(completionPercent([])).toBe(0);
  });

  it("arrondit la part d'éléments faits", () => {
    const items = buildCompletionItems({
      wantsDev: true,
      wantsEntreprise: false,
      profil,
      company: null,
      skillsCount: 0,
    });
    // Seul le profil est créé : 1 élément sur 4
    expect(completionPercent(items)).toBe(25);
  });
});
