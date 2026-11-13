import { describe, expect, it } from "vitest";
import { looksLikeCodeBlock, parseMixedContent } from "./parse-mixed-content";

describe("looksLikeCodeBlock", () => {
  it("détecte un extrait Python", () => {
    expect(
      looksLikeCodeBlock(`def hello():
    return "world"
print(hello())`)
    ).toBe(true);
  });

  it("ignore une phrase normale", () => {
    expect(
      looksLikeCodeBlock(
        "Je n'arrive pas à faire marcher mon formulaire.\nQuelqu'un peut m'aider ?"
      )
    ).toBe(false);
  });
});

describe("parseMixedContent", () => {
  it("extrait un fence markdown avec langage", () => {
    const segments = parseMixedContent(
      "Voici le bug :\n```ts\nconst x = 1;\n```\nMerci"
    );
    expect(segments[0]).toMatchObject({ type: "text" });
    expect(segments[1]).toEqual({
      type: "code",
      value: "const x = 1;",
      language: "ts",
    });
    expect(segments[2]).toMatchObject({ type: "text" });
  });

  it("détecte le code collé sans fence", () => {
    const segments = parseMixedContent(`J'ai ça :

function add(a, b) {
  return a + b;
}

Ça plante.`);
    const code = segments.find((s) => s.type === "code" && !s.inline);
    expect(code?.type).toBe("code");
    if (code?.type === "code") {
      expect(code.value).toContain("function add");
    }
  });

  it("gère le code inline", () => {
    const segments = parseMixedContent("Utilise `useState` ici.");
    expect(segments).toEqual([
      { type: "text", value: "Utilise " },
      { type: "code", value: "useState", inline: true },
      { type: "text", value: " ici." },
    ]);
  });

  it("ne coupe pas un collage Python sur raise ValidationError", () => {
    const source = `class ConversationService:
    """Logique métier des conversations privées (une paire = une conversation)."""

    def __init__(self):
        self.conversation_repository = ConversationRepository()

    @staticmethod
    def _paire_ordonnee(user_a_id: int, user_b_id: int) -> tuple[int, int]:
        if user_a_id == user_b_id:
            raise ValidationError('Impossible de démarrer une conversation avec soi-même.')
        return (min(user_a_id, user_b_id), max(user_a_id, user_b_id))`;

    const segments = parseMixedContent(source);
    const codeBlocks = segments.filter((s) => s.type === "code" && !s.inline);
    expect(codeBlocks).toHaveLength(1);
    if (codeBlocks[0]?.type === "code") {
      expect(codeBlocks[0].value).toContain("raise ValidationError");
      expect(codeBlocks[0].value).toContain("return (min");
    }
  });
});
