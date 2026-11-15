/**
 * Drapeaux SVG de country-flag-icons : un fichier par pays, chargé seulement quand il est affiché
 * (les emojis drapeaux ne s'affichent pas sous Windows).
 */
const FLAG_LOADERS = import.meta.glob<string>("/node_modules/country-flag-icons/3x2/*.svg", {
  query: "?url",
  import: "default",
});

/** Chargeur de l'URL du drapeau d'un pays (undefined si aucun drapeau n'existe pour ce code). */
export function flagLoader(code: string): (() => Promise<string>) | undefined {
  return FLAG_LOADERS[`/node_modules/country-flag-icons/3x2/${code.toUpperCase()}.svg`];
}

/** Vrai si un drapeau existe pour ce code. */
export function hasFlag(code: string): boolean {
  return Boolean(flagLoader(code));
}
