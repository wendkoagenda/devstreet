/**
 * Réglages de style du CV automatique (miroir de backend/app/marketplace/cv_settings.py) et palette de couleurs
 * dérivée de la couleur principale (miroir de `_palette` dans backend/app/marketplace/services/cv_service.py),
 * pour que l'aperçu à l'écran ressemble au PDF.
 */

export type CvFont = "sans" | "serif" | "mono";
export type CvSidebar = "left" | "right";
export type CvSidebarStyle = "filled" | "light";
export type CvPhoto = "round" | "square" | "none";
export type CvSkillStyle = "bars" | "dots" | "text";
export type CvDensity = "compact" | "standard" | "airy";
export type CvSection =
  | "contact"
  | "skills"
  | "languages"
  | "reputation"
  | "bio"
  | "experiences"
  | "prestations";

export type CvSettings = {
  /** Clé d'une couleur proposée (« violet », « bleu »…) ou couleur personnalisée #RRGGBB. */
  color: string;
  font: CvFont;
  sidebar: CvSidebar;
  sidebar_style: CvSidebarStyle;
  photo: CvPhoto;
  skills: CvSkillStyle;
  density: CvDensity;
  hidden_sections: CvSection[];
};

/** Réponse de GET/PATCH/DELETE /marketplace/me/cv-settings. */
export type CvSettingsPayload = {
  settings: CvSettings;
  defaults: CvSettings;
  presets: Record<string, string>;
  sections: CvSection[];
};

type Option<T extends string> = { value: T; label: string };

export const FONT_OPTIONS: (Option<CvFont> & { className: string })[] = [
  { value: "sans", label: "Moderne", className: "font-sans" },
  { value: "serif", label: "Classique", className: "font-serif" },
  { value: "mono", label: "Technique", className: "font-mono" },
];
export const SIDEBAR_OPTIONS: Option<CvSidebar>[] = [
  { value: "left", label: "À gauche" },
  { value: "right", label: "À droite" },
];
export const SIDEBAR_STYLE_OPTIONS: Option<CvSidebarStyle>[] = [
  { value: "filled", label: "Pleine" },
  { value: "light", label: "Claire" },
];
export const PHOTO_OPTIONS: Option<CvPhoto>[] = [
  { value: "round", label: "Ronde" },
  { value: "square", label: "Carrée" },
  { value: "none", label: "Sans" },
];
export const SKILL_OPTIONS: Option<CvSkillStyle>[] = [
  { value: "bars", label: "Barres" },
  { value: "dots", label: "Points" },
  { value: "text", label: "Texte" },
];
export const DENSITY_OPTIONS: Option<CvDensity>[] = [
  { value: "compact", label: "Compacte" },
  { value: "standard", label: "Standard" },
  { value: "airy", label: "Aérée" },
];

export const SECTION_LABELS: Record<CvSection, string> = {
  contact: "Contact",
  skills: "Compétences",
  languages: "Langues",
  reputation: "Réputation",
  bio: "Profil",
  experiences: "Expériences",
  prestations: "Prestations",
};

export const PRESET_LABELS: Record<string, string> = {
  violet: "Violet",
  bleu: "Bleu",
  vert: "Vert",
  orange: "Orange",
  rose: "Rose",
  rouge: "Rouge",
  ardoise: "Ardoise",
};

const HEX_RE = /^#[0-9a-fA-F]{6}$/;

/** Couleur principale effective (#RRGGBB), comme `color_hex` côté serveur. */
export function colorHex(settings: CvSettings, presets: Record<string, string>): string {
  const preset = presets[settings.color];
  if (preset) return preset;
  if (HEX_RE.test(settings.color)) return settings.color.toUpperCase();
  return presets.violet ?? Object.values(presets)[0] ?? "#5D487A";
}

/** Deux réglages identiques (l'ordre des sections masquées ne compte pas). */
export function sameSettings(first: CvSettings, second: CvSettings): boolean {
  const normalize = (settings: CvSettings) =>
    JSON.stringify({ ...settings, hidden_sections: [...settings.hidden_sections].sort() });
  return normalize(first) === normalize(second);
}

/** Réglages passés dans l'adresse du PDF pour un aperçu non enregistré (voir `_preview_settings` côté serveur). */
export function previewQuery(settings: CvSettings): string {
  const params = new URLSearchParams();
  (Object.keys(settings) as (keyof CvSettings)[]).forEach((key) => {
    const value = settings[key];
    params.set(key, Array.isArray(value) ? value.join(",") : value);
  });
  return params.toString();
}

// ── Palette ──

type Rgb = [number, number, number];

const toRgb = (hex: string): Rgb => [
  parseInt(hex.slice(1, 3), 16) / 255,
  parseInt(hex.slice(3, 5), 16) / 255,
  parseInt(hex.slice(5, 7), 16) / 255,
];
const mix = (first: Rgb, second: Rgb, weight: number): Rgb =>
  first.map((value, index) => value * (1 - weight) + second[index] * weight) as Rgb;
const css = ([red, green, blue]: Rgb) =>
  `rgb(${Math.round(red * 255)} ${Math.round(green * 255)} ${Math.round(blue * 255)})`;

// Encre et gris du document (constantes INK et MUTED du rendu PDF) : le CV est une feuille blanche, quel que soit le thème
const INK = toRgb("#1E1B2E");
const MUTED = toRgb("#5B5670");
const WHITE: Rgb = [1, 1, 1];
const BLACK: Rgb = [0, 0, 0];

export type CvPalette = {
  main: string;
  soft: string;
  border: string;
  accentBar: string;
  ink: string;
  muted: string;
  paper: string;
  side: {
    bg: string;
    text: string;
    muted: string;
    track: string;
    fill: string;
    ring: string;
    initialsBg: string;
    initialsText: string;
    heading: string;
  };
};

/** Couleurs du CV dérivées de la couleur principale (bande pleine : texte clair ou foncé selon la luminosité). */
export function cvPalette(settings: CvSettings, presets: Record<string, string>): CvPalette {
  const main = toRgb(colorHex(settings, presets));
  const luminance = 0.2126 * main[0] + 0.7152 * main[1] + 0.0722 * main[2];
  const soft = mix(main, WHITE, 0.94);
  let side: Omit<CvPalette["side"], "heading" | "initialsText"> & { textRgb: Rgb; ringRgb: Rgb };
  if (settings.sidebar_style === "filled") {
    const darkText = luminance > 0.55;
    const on = darkText ? INK : mix(main, WHITE, 0.95);
    const contrast = darkText ? BLACK : WHITE;
    side = {
      bg: css(main),
      text: css(on),
      muted: css(mix(on, main, 0.35)),
      track: css(mix(main, contrast, 0.25)),
      fill: css(on),
      ring: css(on),
      initialsBg: css(mix(main, contrast, 0.2)),
      textRgb: on,
      ringRgb: on,
    };
  } else {
    side = {
      bg: css(soft),
      text: css(INK),
      muted: css(MUTED),
      track: css(mix(main, WHITE, 0.8)),
      fill: css(main),
      ring: css(main),
      initialsBg: css(main),
      textRgb: INK,
      ringRgb: main,
    };
  }
  const { textRgb, ringRgb, ...sideColors } = side;
  const sameAsRing = textRgb.every((value, index) => value === ringRgb[index]);
  return {
    main: css(main),
    soft: css(soft),
    border: css(mix(main, WHITE, 0.82)),
    accentBar: css(mix(main, WHITE, 0.18)),
    ink: css(INK),
    muted: css(MUTED),
    paper: css(WHITE),
    side: {
      ...sideColors,
      initialsText: sameAsRing ? css(WHITE) : sideColors.text,
      heading: settings.sidebar_style === "filled" ? sideColors.text : css(main),
    },
  };
}
