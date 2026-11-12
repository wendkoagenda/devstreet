// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";

vi.mock("@/helpers/api/csrf", () => ({ API_URL: "https://api.exemple.fr/api" }));
vi.mock("@/config/config", () => ({ default: { gcs: { bucket_name: undefined } } }));

import {
  buildGcsUrl,
  buildLocalUrl,
  extractFilePathFromUrl,
} from "./media-url-builder";

describe("media-url-builder : plus de serveur codé en dur", () => {
  it("construit les URL locales à partir de l'origine de VITE_API_URL", () => {
    expect(buildLocalUrl("photo.png")).toBe("https://api.exemple.fr/media/photo.png");
  });

  it("refuse de construire une URL GCS sans bucket configuré", () => {
    expect(() => buildGcsUrl("photo.png")).toThrow("VITE_GCS_BUCKET_NAME");
  });

  it("extrait le chemin d'une URL GCS ou locale", () => {
    expect(extractFilePathFromUrl("https://storage.googleapis.com/bucket/a/b.png")).toBe("a/b.png");
    expect(extractFilePathFromUrl("/media/a/b.png")).toBe("a/b.png");
  });

  it("retourne null pour une URL qui n'est ni GCS ni locale", () => {
    expect(extractFilePathFromUrl("https://exemple.fr/x.png")).toBeNull();
  });
});
