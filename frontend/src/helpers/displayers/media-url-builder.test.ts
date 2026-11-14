// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";

const mockConfig = vi.hoisted(() => ({ storage: { use_s3: false } }));

vi.mock("@/helpers/api/csrf", () => ({ API_URL: "https://api.exemple.fr/api" }));
vi.mock("@/config/config", () => ({ default: mockConfig }));

import {
  buildFilesUrl,
  buildLocalUrl,
  buildMediaUrl,
  extractFilePathFromUrl,
} from "./media-url-builder";

describe("media-url-builder : plus de serveur codé en dur", () => {
  beforeEach(() => {
    mockConfig.storage.use_s3 = false;
  });

  it("construit les URL locales à partir de l'origine de VITE_API_URL", () => {
    expect(buildLocalUrl("photo.png")).toBe("https://api.exemple.fr/media/photo.png");
  });

  it("sert un chemin relatif depuis /media/ quand S3 est inactif", () => {
    expect(buildMediaUrl("forum_images/photo.png")).toBe("https://api.exemple.fr/media/forum_images/photo.png");
  });

  it("sert un chemin relatif via /api/v1/files/ quand S3 est actif (bucket privé)", () => {
    mockConfig.storage.use_s3 = true;
    expect(buildMediaUrl("forum_images/photo.png")).toBe("https://api.exemple.fr/api/v1/files/forum_images/photo.png");
  });

  it("encode les segments du chemin sans toucher aux « / »", () => {
    expect(buildFilesUrl("forum_images/ma photo é.png")).toBe(
      "https://api.exemple.fr/api/v1/files/forum_images/ma%20photo%20%C3%A9.png",
    );
  });

  it("ramène une URL /api/v1/files/ ou /media/ relative vers le backend, et laisse les URL absolues", () => {
    expect(buildMediaUrl("/api/v1/files/a/b.png")).toBe("https://api.exemple.fr/api/v1/files/a/b.png");
    expect(buildMediaUrl("/media/a/b.png")).toBe("https://api.exemple.fr/media/a/b.png");
    expect(buildMediaUrl("https://autre.exemple.fr/x.png")).toBe("https://autre.exemple.fr/x.png");
  });

  it("extrait le chemin (encodé) d'une URL /api/v1/files/ ou /media/", () => {
    expect(extractFilePathFromUrl("https://api.exemple.fr/api/v1/files/a/ma%20photo.png")).toBe("a/ma%20photo.png");
    expect(extractFilePathFromUrl("/media/a/b.png")).toBe("a/b.png");
  });

  it("retourne null pour une URL qui n'est ni /api/v1/files/ ni /media/", () => {
    expect(extractFilePathFromUrl("https://exemple.fr/x.png")).toBeNull();
  });
});
