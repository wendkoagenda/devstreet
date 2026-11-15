import { useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { PublicProfile } from "@/models/marketplace-network/schema";
import { FONT_OPTIONS, type CvPalette, type CvSection, type CvSettings } from "../cv-settings";

/**
 * Aperçu du CV automatique : une feuille A4 qui reprend la mise en page du PDF (bande latérale + colonne principale)
 * et suit les réglages de style en direct. Les mesures sont celles du PDF converties en pixels (1 cm = 37,8 px).
 */

const CM = 37.8;
const PT = 4 / 3;
const PAGE_W = 21 * CM;
const PAGE_H = 29.7 * CM;
const SIDEBAR_W = 6.6 * CM;
const SIDE_PAD = 0.75 * CM;
const MAIN_GAP = 0.9 * CM;
const MAIN_MARGIN = 1.5 * CM;
const PHOTO = 3.7 * CM;
const MAX_SKILLS = 14;

const FONT_SCALE: Record<CvSettings["font"], number> = { sans: 1, serif: 1.06, mono: 0.92 };
const DENSITY_SCALE: Record<CvSettings["density"], number> = { compact: 0.9, standard: 1, airy: 1.14 };

const shortLink = (url: string) => url.replace(/^https?:\/\//, "").replace(/\/$/, "");
const initialsOf = (name: string) =>
  name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0] ?? "")
    .join("")
    .toUpperCase() || "?";

type CvDocumentProps = {
  profile: PublicProfile;
  phone?: string;
  photoUrl?: string | null;
  settings: CvSettings;
  palette: CvPalette;
};

export function CvDocument({ profile, phone, photoUrl, settings, palette }: CvDocumentProps) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language?.startsWith("en") ? "en-GB" : "fr-FR";
  const month = (value: string) =>
    new Date(value).toLocaleDateString(locale, { month: "short", year: "numeric" });
  const fontScale = FONT_SCALE[settings.font];
  const density = DENSITY_SCALE[settings.density];
  const fontClass = FONT_OPTIONS.find((option) => option.value === settings.font)?.className;
  const show = (section: CvSection) => !settings.hidden_sections.includes(section);
  const sideLeft = settings.sidebar === "left";
  const side = palette.side;

  /** Texte au format PDF : taille en points, interligne en points (multiplié par la densité). */
  const text = (size: number, lead: number, extra: CSSProperties = {}): CSSProperties => ({
    fontSize: size * fontScale * PT,
    lineHeight: `${lead * fontScale * density * PT}px`,
    ...extra,
  });
  const space = (pt: number) => pt * density * PT;

  const sideHeading = (label: string) => (
    <p
      style={text(9.5, 12, {
        color: side.heading,
        fontWeight: 700,
        letterSpacing: "0.08em",
        marginTop: space(14),
        marginBottom: space(4),
      })}
    >
      {label}
    </p>
  );
  const mainHeading = (label: string) => (
    <p
      style={text(10.5, 13, {
        color: palette.main,
        fontWeight: 700,
        letterSpacing: "0.08em",
        marginTop: space(15),
        marginBottom: space(3),
      })}
    >
      {label.toUpperCase()}
    </p>
  );

  const location = [profile.city, profile.country].filter(Boolean).join(", ");
  const contactLines = [profile.email, phone, location].filter(Boolean) as string[];
  const links = [profile.github_url, profile.linkedin_url, profile.portfolio_url].filter(Boolean);
  const skills = profile.skills_detail.slice(0, MAX_SKILLS);
  const sideWidth = SIDEBAR_W - 2 * SIDE_PAD;

  // ── Bande latérale ──
  const sidebar = (
    <div style={{ width: sideWidth }}>
      <div style={{ height: 0.2 * CM }} />
      {settings.photo !== "none" ? (
        <div
          className={cn("mx-auto flex items-center justify-center overflow-hidden")}
          style={{
            width: PHOTO + 6,
            height: PHOTO + 6,
            padding: 3,
            background: side.ring,
            borderRadius: settings.photo === "round" ? "9999px" : (PHOTO + 6) * 0.1,
          }}
        >
          {photoUrl ? (
            <img
              src={photoUrl}
              alt=""
              className="size-full object-cover"
              style={{ borderRadius: settings.photo === "round" ? "9999px" : PHOTO * 0.1 }}
            />
          ) : (
            <div
              className="flex size-full items-center justify-center"
              style={{
                background: side.initialsBg,
                color: side.initialsText,
                borderRadius: settings.photo === "round" ? "9999px" : PHOTO * 0.1,
                fontSize: PHOTO * 0.34,
                fontWeight: 700,
              }}
            >
              {initialsOf(profile.name)}
            </div>
          )}
        </div>
      ) : null}

      {show("contact") && (contactLines.length > 0 || links.length > 0) ? (
        <>
          {sideHeading(t("marketplace.cv.doc_contact"))}
          {[...contactLines, ...links.map(shortLink)].map((line) => (
            <p key={line} className="break-words" style={text(8.8, 12.5, { color: side.text, marginBottom: 2 })}>
              {line}
            </p>
          ))}
        </>
      ) : null}

      {show("skills") && skills.length > 0 ? (
        <>
          {sideHeading(t("marketplace.cv.doc_skills"))}
          {skills.map((skill) => (
            <SkillLine
              key={skill.name}
              style={settings.skills}
              name={skill.name}
              level={skill.level}
              palette={palette}
              text={text}
            />
          ))}
        </>
      ) : null}

      {show("languages") && profile.languages.length > 0 ? (
        <>
          {sideHeading(t("marketplace.cv.doc_languages"))}
          {profile.languages.map((language) => (
            <p key={language} style={text(8.8, 12.5, { color: side.text })}>
              {language}
            </p>
          ))}
        </>
      ) : null}

      {profile.years_of_experience ? (
        <>
          {sideHeading(t("marketplace.cv.doc_experience"))}
          <p style={text(8.8, 12.5, { color: side.text })}>
            {t("marketplace.cv.doc_years", { count: profile.years_of_experience })}
          </p>
        </>
      ) : null}

      {show("reputation") && profile.rating_avg !== null ? (
        <>
          {sideHeading(t("marketplace.cv.doc_reputation"))}
          <p style={text(8.8, 12.5, { color: side.text })}>{profile.rating_avg} / 5</p>
          <p style={text(8.2, 11.5, { color: side.muted })}>
            {t("marketplace.cv.doc_public_reviews", { count: profile.reviews_count })}
          </p>
        </>
      ) : null}
    </div>
  );

  // ── Colonne principale ──
  const mainWidth = PAGE_W - SIDEBAR_W - MAIN_GAP - MAIN_MARGIN;
  const main = (
    <div style={{ width: mainWidth }}>
      <p style={text(26, 29, { color: palette.ink, fontWeight: 700 })}>{profile.name}</p>
      {profile.headline ? (
        <p style={text(12.5, 17, { color: palette.main, marginTop: space(3) })}>{profile.headline}</p>
      ) : null}
      <div style={{ height: 1.6, background: palette.border, marginTop: 7, marginBottom: 3 }} />

      {show("bio") && profile.bio ? (
        <>
          {mainHeading(t("marketplace.cv.doc_profile"))}
          <p className="whitespace-pre-line" style={text(9.8, 14, { color: palette.ink })}>
            {profile.bio}
          </p>
        </>
      ) : null}

      {show("experiences") && profile.experiences.length > 0 ? (
        <>
          {mainHeading(t("marketplace.cv.doc_experiences"))}
          {profile.experiences.map((experience) => (
            <div key={experience.id} style={{ marginTop: 7 }}>
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p style={text(10.5, 13.5, { color: palette.ink, fontWeight: 700 })}>{experience.title}</p>
                  <p style={text(9.8, 13, { color: palette.main })}>{experience.company_name}</p>
                </div>
                <p className="shrink-0 text-right" style={text(8.8, 12, { color: palette.muted, width: 3.3 * CM })}>
                  {month(experience.start_date)} –{" "}
                  {experience.is_current || !experience.end_date
                    ? t("marketplace.cv.doc_today")
                    : month(experience.end_date)}
                </p>
              </div>
              {experience.location ? (
                <p style={text(8.8, 12, { color: palette.muted })}>{experience.location}</p>
              ) : null}
              {experience.description ? (
                <p className="whitespace-pre-line" style={text(9.8, 14, { color: palette.ink })}>
                  {experience.description}
                </p>
              ) : null}
              {experience.technologies ? (
                <p style={text(8.8, 12, { color: palette.muted })}>
                  {t("marketplace.cv.doc_technologies", { list: experience.technologies })}
                </p>
              ) : null}
            </div>
          ))}
        </>
      ) : null}
    </div>
  );

  return (
    <ScaledPage>
      <div
        className={cn("relative overflow-hidden text-left", fontClass)}
        style={{ width: PAGE_W, minHeight: PAGE_H, background: palette.paper, color: palette.ink }}
      >
        {/* Bande latérale (fond) et liseré d'accent en haut de la colonne principale */}
        <div
          className="absolute inset-y-0"
          style={{
            width: SIDEBAR_W,
            left: sideLeft ? 0 : undefined,
            right: sideLeft ? undefined : 0,
            background: side.bg,
            borderRight: sideLeft && settings.sidebar_style === "light" ? `1px solid ${palette.border}` : undefined,
            borderLeft: !sideLeft && settings.sidebar_style === "light" ? `1px solid ${palette.border}` : undefined,
          }}
        />
        <div
          className="absolute top-0"
          style={{
            height: 0.28 * CM,
            width: PAGE_W - SIDEBAR_W,
            left: sideLeft ? SIDEBAR_W : 0,
            background: palette.accentBar,
          }}
        />
        <div
          className="relative flex items-start"
          style={{ flexDirection: sideLeft ? "row" : "row-reverse", paddingTop: 1.2 * CM, paddingBottom: 1.2 * CM }}
        >
          <div style={{ width: SIDEBAR_W, paddingLeft: SIDE_PAD, paddingRight: SIDE_PAD }}>{sidebar}</div>
          <div
            style={{
              paddingTop: 0.3 * CM,
              marginLeft: sideLeft ? MAIN_GAP : MAIN_MARGIN,
              marginRight: sideLeft ? MAIN_MARGIN : MAIN_GAP,
            }}
          >
            {main}
          </div>
        </div>
      </div>
    </ScaledPage>
  );
}

type TextStyle = (size: number, lead: number, extra?: CSSProperties) => CSSProperties;

function SkillLine({
  style,
  name,
  level,
  palette,
  text,
}: {
  style: CvSettings["skills"];
  name: string;
  level: number;
  palette: CvPalette;
  text: TextStyle;
}) {
  const { t } = useTranslation();
  const side = palette.side;
  const value = Math.max(0, Math.min(5, level));
  const levelLabel =
    value >= 1 && value <= 5
      ? t(`marketplace.cv.level.${value}`)
      : String(value);
  if (style === "text") {
    return (
      <p style={text(8.8, 12.5, { color: side.text })}>
        {name} <span style={{ color: side.muted }}>· {levelLabel}</span>
      </p>
    );
  }
  if (style === "dots") {
    return (
      <div className="flex items-center justify-between gap-2" style={{ height: 0.52 * CM }}>
        <span className="truncate" style={text(8.6, 11, { color: side.text })}>
          {name}
        </span>
        <span
          className="flex shrink-0"
          style={{ gap: 4.5 }}
          aria-label={t("marketplace.cv.doc_level_aria", { value })}
        >
          {[0, 1, 2, 3, 4].map((index) => (
            <span
              key={index}
              className="rounded-full"
              style={{ width: 6, height: 6, background: index < value ? side.fill : side.track }}
            />
          ))}
        </span>
      </div>
    );
  }
  return (
    <div
      style={{ height: 0.78 * CM }}
      aria-label={t("marketplace.cv.doc_skill_level_aria", { name, value })}
    >
      <p className="truncate" style={text(8.6, 11, { color: side.text })}>
        {name}
      </p>
      <div className="mt-1 overflow-hidden rounded-full" style={{ height: 4.3, background: side.track }}>
        <div className="h-full rounded-full" style={{ width: `${(value / 5) * 100}%`, background: side.fill }} />
      </div>
    </div>
  );
}

/** Affiche la feuille A4 à la largeur disponible (réduite sur petit écran, jamais agrandie). */
function ScaledPage({ children }: { children: ReactNode }) {
  const outer = useRef<HTMLDivElement>(null);
  const inner = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [height, setHeight] = useState(PAGE_H);

  useLayoutEffect(() => {
    const measure = () => {
      if (!outer.current || !inner.current) return;
      const next = Math.min(1, outer.current.clientWidth / PAGE_W);
      setScale(next);
      setHeight(inner.current.offsetHeight * next);
    };
    measure();
    const observer = new ResizeObserver(measure);
    if (outer.current) observer.observe(outer.current);
    if (inner.current) observer.observe(inner.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={outer} className="w-full" style={{ height }}>
      <div
        ref={inner}
        className="mx-auto origin-top-left overflow-hidden rounded-sm shadow-xl ring-1 ring-border"
        style={{ width: PAGE_W, transform: `scale(${scale})` }}
      >
        {children}
      </div>
    </div>
  );
}
