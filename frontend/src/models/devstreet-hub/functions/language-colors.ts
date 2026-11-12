/** Couleurs type linguist pour la barre / pastilles de langues détectées. */
const LANGUAGE_COLORS: Record<string, string> = {
  HTML: "#e34c26",
  CSS: "#563d7c",
  JavaScript: "#f1e05a",
  TypeScript: "#3178c6",
  Python: "#3572A5",
  Go: "#00ADD8",
  Java: "#b07219",
  Ruby: "#701516",
  PHP: "#4F5D95",
  Rust: "#dea584",
  Shell: "#89e051",
  Dockerfile: "#384d54",
  Markdown: "#083fa1",
  JSON: "#292929",
  YAML: "#cb171e",
  Vue: "#41b883",
  SCSS: "#c6538c",
  SQL: "#e38c00",
  C: "#555555",
  "C++": "#f34b7d",
  "C#": "#178600",
  Kotlin: "#A97BFF",
  Swift: "#F05138",
  Dart: "#00B4AB",
};

const FALLBACK = [
  "#e34c26",
  "#3572A5",
  "#f1e05a",
  "#563d7c",
  "#00ADD8",
  "#b07219",
];

export function languageColor(name: string): string {
  if (LANGUAGE_COLORS[name]) return LANGUAGE_COLORS[name];
  const key = Object.keys(LANGUAGE_COLORS).find(
    (item) => item.toLowerCase() === name.toLowerCase()
  );
  if (key) return LANGUAGE_COLORS[key];
  let hash = 0;
  for (let i = 0; i < name.length; i += 1) {
    hash = (hash + name.charCodeAt(i) * (i + 1)) % 997;
  }
  return FALLBACK[hash % FALLBACK.length];
}
