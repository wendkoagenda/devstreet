import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Check, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import { CV_VISIBILITIES } from "@/models/marketplace-space/options";
import {
  DENSITY_OPTIONS,
  FONT_OPTIONS,
  PHOTO_OPTIONS,
  SIDEBAR_OPTIONS,
  SIDEBAR_STYLE_OPTIONS,
  SKILL_OPTIONS,
  colorHex,
  type CvSection,
  type CvSettings,
} from "../cv-settings";

type CvSettingsSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  settings: CvSettings;
  presets: Record<string, string>;
  sections: CvSection[];
  onChange: (changes: Partial<CvSettings>) => void;
  dirty: boolean;
  saving: boolean;
  onSave: () => void;
  onDiscard: () => void;
  onReset: () => void;
  visibility?: string;
  onVisibilityChange: (value: string) => void;
  visibilitySaving: boolean;
};

/** Panneau « Personnaliser mon CV » : les changements s'affichent en direct dans l'aperçu, puis s'enregistrent. */
export function CvSettingsSheet({
  open,
  onOpenChange,
  settings,
  presets,
  sections,
  onChange,
  dirty,
  saving,
  onSave,
  onDiscard,
  onReset,
  visibility,
  onVisibilityChange,
  visibilitySaving,
}: CvSettingsSheetProps) {
  const { t } = useTranslation();
  const current = colorHex(settings, presets);
  const isCustom = !presets[settings.color];
  const presetName = (key: string) => t(`marketplace.cv.preset.${key}`, { defaultValue: key });
  const toggleSection = (section: CvSection, visible: boolean) => {
    const hidden = settings.hidden_sections.filter((item) => item !== section);
    onChange({ hidden_sections: visible ? hidden : [...hidden, section] });
  };

  const photoOptions = PHOTO_OPTIONS.map((option) => ({
    ...option,
    label: t(`marketplace.cv.photo_opt.${option.value}`),
  }));
  const skillOptions = SKILL_OPTIONS.map((option) => ({
    ...option,
    label: t(`marketplace.cv.skill_opt.${option.value}`),
  }));
  const densityOptions = DENSITY_OPTIONS.map((option) => ({
    ...option,
    label: t(`marketplace.cv.density_opt.${option.value}`),
  }));

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="flex w-full flex-col gap-0 p-0 sm:max-w-md">
        <SheetHeader className="border-b border-border px-6 py-5 text-left">
          <SheetTitle>{t("marketplace.cv.customize_title")}</SheetTitle>
          <SheetDescription>{t("marketplace.cv.customize_desc")}</SheetDescription>
        </SheetHeader>

        <div className="flex-1 space-y-6 overflow-y-auto px-6 py-5">
          <Group title={t("marketplace.cv.color")}>
            <div className="flex flex-wrap items-center gap-2.5">
              {Object.entries(presets).map(([key, hex]) => (
                <button
                  key={key}
                  type="button"
                  title={presetName(key)}
                  aria-label={t("marketplace.cv.color_aria", { name: presetName(key) })}
                  aria-pressed={settings.color === key}
                  onClick={() => onChange({ color: key })}
                  className={cn(
                    "flex size-9 items-center justify-center rounded-full ring-offset-2 ring-offset-background transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                    settings.color === key ? "ring-2 ring-foreground" : "hover:scale-110",
                  )}
                  style={{ background: hex }}
                >
                  {settings.color === key ? <Check className="size-4 text-primary-foreground" /> : null}
                </button>
              ))}
              <label
                className={cn(
                  "relative flex size-9 cursor-pointer items-center justify-center overflow-hidden rounded-full border border-dashed border-border ring-offset-2 ring-offset-background transition focus-within:ring-2 focus-within:ring-ring",
                  isCustom && "border-solid ring-2 ring-foreground",
                )}
                title={t("marketplace.cv.color_custom")}
                style={isCustom ? { background: current } : undefined}
              >
                {isCustom ? null : <span className="text-xs font-semibold text-muted-foreground">+</span>}
                <input
                  type="color"
                  aria-label={t("marketplace.cv.color_custom")}
                  value={current.toLowerCase()}
                  onChange={(event) => onChange({ color: event.target.value.toUpperCase() })}
                  className="absolute inset-0 size-full cursor-pointer opacity-0"
                />
              </label>
            </div>
            <p className="text-xs text-muted-foreground">
              {isCustom
                ? t("marketplace.cv.color_custom_label", { hex: current })
                : `${presetName(settings.color)} · ${current}`}
            </p>
          </Group>

          <Group title={t("marketplace.cv.font")}>
            <div className="grid grid-cols-3 gap-2">
              {FONT_OPTIONS.map((option) => (
                <OptionCard
                  key={option.value}
                  selected={settings.font === option.value}
                  onClick={() => onChange({ font: option.value })}
                >
                  <span className={cn("text-2xl leading-none text-foreground", option.className)}>Aa</span>
                  <span className="text-xs text-muted-foreground">
                    {t(`marketplace.cv.font_opt.${option.value}`)}
                  </span>
                </OptionCard>
              ))}
            </div>
          </Group>

          <Group title={t("marketplace.cv.layout")}>
            <div className="grid grid-cols-2 gap-2">
              {SIDEBAR_OPTIONS.flatMap((position) =>
                SIDEBAR_STYLE_OPTIONS.map((style) => {
                  const selected =
                    settings.sidebar === position.value && settings.sidebar_style === style.value;
                  return (
                    <OptionCard
                      key={`${position.value}-${style.value}`}
                      selected={selected}
                      onClick={() =>
                        onChange({ sidebar: position.value, sidebar_style: style.value })
                      }
                    >
                      <LayoutThumbnail
                        color={current}
                        side={position.value}
                        filled={style.value === "filled"}
                      />
                      <span className="text-xs text-muted-foreground">
                        {t("marketplace.cv.band_layout", {
                          style: t(`marketplace.cv.sidebar_style.${style.value}`).toLowerCase(),
                          side: t(`marketplace.cv.sidebar.${position.value}`).toLowerCase(),
                        })}
                      </span>
                    </OptionCard>
                  );
                }),
              )}
            </div>
          </Group>

          <Group title={t("marketplace.cv.photo")}>
            <Segmented
              options={photoOptions}
              value={settings.photo}
              onChange={(photo) => onChange({ photo })}
            />
          </Group>

          <Group title={t("marketplace.cv.skills")}>
            <Segmented
              options={skillOptions}
              value={settings.skills}
              onChange={(skills) => onChange({ skills })}
            />
          </Group>

          <Group title={t("marketplace.cv.density")}>
            <Segmented
              options={densityOptions}
              value={settings.density}
              onChange={(density) => onChange({ density })}
            />
          </Group>

          <Group title={t("marketplace.cv.sections")}>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2.5">
              {sections.map((section) => {
                const id = `cv-section-${section}`;
                return (
                  <div key={section} className="flex items-center gap-2">
                    <Checkbox
                      id={id}
                      checked={!settings.hidden_sections.includes(section)}
                      onCheckedChange={(checked) => toggleSection(section, checked === true)}
                    />
                    <Label htmlFor={id} className="text-sm font-normal">
                      {t(`marketplace.cv.section.${section}`)}
                    </Label>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-muted-foreground">{t("marketplace.cv.sections_hint")}</p>
          </Group>

          <Separator />

          <Group title={t("marketplace.cv.who_can_download")}>
            <Select value={visibility} onValueChange={onVisibilityChange} disabled={visibilitySaving}>
              <SelectTrigger aria-label={t("marketplace.cv.visibility_aria")}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CV_VISIBILITIES.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">{t("marketplace.cv.saved_immediately")}</p>
          </Group>
        </div>

        <SheetFooter className="flex-row items-center justify-between gap-2 border-t border-border px-6 py-4 sm:justify-between">
          <Button type="button" variant="ghost" size="sm" onClick={onReset} disabled={saving}>
            <RotateCcw className="size-4" />
            {t("marketplace.cv.original_style")}
          </Button>
          <div className="flex gap-2">
            <Button type="button" variant="outline" size="sm" onClick={onDiscard} disabled={!dirty || saving}>
              {t("actions.cancel")}
            </Button>
            <Button type="button" size="sm" onClick={onSave} disabled={!dirty || saving}>
              {t("actions.save")}
            </Button>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

function Group({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{title}</h3>
      {children}
    </section>
  );
}

function OptionCard({
  selected,
  onClick,
  children,
}: {
  selected: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={cn(
        "flex flex-col items-center gap-2 rounded-lg border p-3 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        selected ? "border-primary bg-primary/5 shadow-sm" : "border-border hover:border-primary/40 hover:bg-muted",
      )}
    >
      {children}
    </button>
  );
}

function Segmented<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <div className="grid rounded-lg bg-muted p-1" style={{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={value === option.value}
          onClick={() => onChange(option.value)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            value === option.value
              ? "bg-background font-medium text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

/** Vignette de page : bande latérale pleine ou claire, à gauche ou à droite, dans la couleur choisie. */
function LayoutThumbnail({ color, side, filled }: { color: string; side: "left" | "right"; filled: boolean }) {
  return (
    <div
      className={cn("flex h-16 w-12 overflow-hidden rounded-sm border border-border bg-background", side === "right" && "flex-row-reverse")}
      aria-hidden
    >
      <div className="h-full w-[32%]" style={{ background: color, opacity: filled ? 1 : 0.14 }} />
      <div className="flex flex-1 flex-col gap-1 p-1.5">
        <div className="h-1 w-3/4 rounded-full" style={{ background: color, opacity: 0.85 }} />
        <div className="h-0.5 w-full rounded-full bg-muted-foreground/30" />
        <div className="h-0.5 w-5/6 rounded-full bg-muted-foreground/30" />
        <div className="h-0.5 w-full rounded-full bg-muted-foreground/30" />
      </div>
    </div>
  );
}
