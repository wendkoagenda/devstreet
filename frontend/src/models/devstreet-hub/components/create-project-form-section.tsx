import { ChevronDown, ChevronUp } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PROJECT_LICENSES, type ProjectLicense } from "../schema";
import type { CreateProjectFormState } from "../hooks/use-create-project";

interface CreateProjectFormSectionProps {
  form: CreateProjectFormState;
  locked: boolean;
  onPatch: (patch: Partial<CreateProjectFormState>) => void;
}

export function CreateProjectFormSection({
  form,
  locked,
  onPatch,
}: CreateProjectFormSectionProps) {
  const { t } = useTranslation();

  return (
    <section
      aria-labelledby="create-form-title"
      className="flex flex-col gap-6 rounded-2xl border border-border bg-card p-6 shadow-card sm:p-7"
    >
      <div className="border-b border-border pb-4">
        <h2 className="text-base font-bold text-foreground" id="create-form-title">
          {t("hub.create.sections.presentation")}
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          {t("hub.create.sections.presentation_hint")}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5 sm:col-span-2">
          <Label htmlFor="project-title">
            {t("hub.create.fields.title")} <span className="text-brand">*</span>
          </Label>
          <Input
            id="project-title"
            value={form.title}
            onChange={(event) => onPatch({ title: event.target.value })}
            className="h-10 bg-secondary font-semibold"
            maxLength={180}
            required
            disabled={locked}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="project-license">{t("hub.create.fields.license")}</Label>
          <Select
            value={form.declared_license}
            disabled={locked}
            onValueChange={(value) =>
              onPatch({ declared_license: value as ProjectLicense })
            }
          >
            <SelectTrigger
              id="project-license"
              className="h-10 rounded-lg bg-secondary text-xs font-medium shadow-none focus:border-brand focus:ring-brand"
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="rounded-lg">
              {PROJECT_LICENSES.map((license) => (
                <SelectItem key={license} value={license} className="text-xs">
                  {t(`hub.create.licenses.${license}`, { defaultValue: license })}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <p className="sm:col-span-2 text-xs leading-relaxed text-muted-foreground">
          {t("hub.create.fields.technologies_auto")}
        </p>
      </div>

      <div className="border-t border-border pt-2">
        <Button
          type="button"
          variant="ghost"
          disabled={locked}
          className="h-8 gap-1.5 px-2 text-xs text-muted-foreground"
          onClick={() => onPatch({ showAdvanced: !form.showAdvanced })}
        >
          {form.showAdvanced ? (
            <ChevronUp aria-hidden className="size-3.5" />
          ) : (
            <ChevronDown aria-hidden className="size-3.5" />
          )}
          {t("hub.create.advanced.toggle")}
        </Button>

        {form.showAdvanced ? (
          <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="project-slug">{t("hub.create.fields.slug")}</Label>
              <Input
                id="project-slug"
                value={form.slug}
                disabled={locked}
                onChange={(event) =>
                  onPatch({
                    slug: event.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ""),
                    slugTouched: true,
                  })
                }
                className="h-10 bg-secondary font-semibold text-brand"
                maxLength={100}
                placeholder={t("hub.create.fields.slug_auto")}
              />
              <span className="text-[11px] text-muted-foreground">
                {t("hub.create.fields.slug_hint")}
              </span>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="project-demo">{t("hub.create.fields.demo_url")}</Label>
              <Input
                id="project-demo"
                type="url"
                disabled={locked}
                value={form.demo_url}
                onChange={(event) => onPatch({ demo_url: event.target.value })}
                className="h-10 bg-secondary"
                placeholder="https://"
              />
            </div>

            <div className="flex flex-col gap-1.5 sm:col-span-2">
              <Label htmlFor="project-problem">{t("hub.create.fields.problem")}</Label>
              <Input
                id="project-problem"
                disabled={locked}
                value={form.problem}
                onChange={(event) => onPatch({ problem: event.target.value })}
                className="h-10 bg-secondary"
                maxLength={140}
              />
            </div>

            <div className="flex flex-col gap-1.5 sm:col-span-2">
              <Label htmlFor="project-description">
                {t("hub.create.fields.description")}
              </Label>
              <Textarea
                id="project-description"
                disabled={locked}
                value={form.description}
                onChange={(event) => onPatch({ description: event.target.value })}
                className="min-h-[88px] resize-none bg-secondary text-xs leading-relaxed"
                rows={3}
              />
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
