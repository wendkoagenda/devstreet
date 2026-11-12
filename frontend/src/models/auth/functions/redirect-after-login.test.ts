// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from "vitest";
import {
  clearRedirectPath,
  consumeRedirectPath,
  DEFAULT_REDIRECT_PATH,
  isSafeRedirectPath,
  peekRedirectPath,
  REDIRECT_STORAGE_KEY,
  saveRedirectPath,
} from "./redirect-after-login";

describe("redirect-after-login", () => {
  beforeEach(() => {
    sessionStorage.clear();
    window.history.pushState({}, "", "/");
  });

  it("sauvegarde la page courante avec sa query string et son ancre", () => {
    window.history.pushState({}, "", "/elitests?page=2&q=abc#details");
    saveRedirectPath();
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBe(
      "/elitests?page=2&q=abc#details"
    );
  });

  it("peekRedirectPath lit sans effacer", () => {
    saveRedirectPath("/roles");
    expect(peekRedirectPath()).toBe("/roles");
    expect(peekRedirectPath()).toBe("/roles");
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBe("/roles");
  });

  it("restitue le chemin une seule fois", () => {
    saveRedirectPath("/users");
    expect(consumeRedirectPath()).toBe("/users");
    expect(consumeRedirectPath()).toBe(DEFAULT_REDIRECT_PATH);
  });

  it("retourne le repli quand rien n'est sauvegardé", () => {
    expect(consumeRedirectPath()).toBe(DEFAULT_REDIRECT_PATH);
    expect(consumeRedirectPath("/")).toBe("/");
  });

  it("n'enregistre jamais les pages publiques d'authentification", () => {
    saveRedirectPath("/login");
    saveRedirectPath("/login?next=/users");
    saveRedirectPath("/forgot-password");
    saveRedirectPath("/forgot-password?step=code");
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });

  it("refuse les redirections vers un site externe", () => {
    for (const bad of [
      "https://evil.example/phish",
      "//evil.example",
      "/\\evil.example",
      "javascript:alert(1)",
      "users",
      "",
    ]) {
      expect(isSafeRedirectPath(bad)).toBe(false);
    }
    // une valeur piégée déjà présente dans le stockage est ignorée
    sessionStorage.setItem(REDIRECT_STORAGE_KEY, "//evil.example");
    expect(consumeRedirectPath()).toBe(DEFAULT_REDIRECT_PATH);
  });

  it("clearRedirectPath efface la sauvegarde", () => {
    saveRedirectPath("/roles");
    clearRedirectPath();
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });
});
