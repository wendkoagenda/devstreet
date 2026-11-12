/**
 * Relation imbriquée renvoyée par le backend (serializers en depth=1) : l'identifiant et les champs du modèle lié.
 * En écriture, le backend attend l'identifiant dans « <champ>_id » (ex. company_id).
 */
export type RelationRef = { id: number } & Record<string, unknown>;

/** Libellé lisible d'une relation imbriquée : premier champ texte non vide parmi `keys`, sinon « #id ». */
export const relationLabel = (
  ref: RelationRef | null | undefined,
  keys: string[]
): string => {
  if (!ref) return "—";
  for (const key of keys) {
    const value = ref[key];
    if (typeof value === "string" && value.trim() !== "") return value;
  }
  return `#${ref.id}`;
};
