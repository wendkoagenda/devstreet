import { ArrowRight, Globe } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface CreateProjectPublishSectionProps {
  integrityConfirmed: boolean;
  canPublish: boolean;
  repoReady: boolean;
  isBusy: boolean;
  projectSlug: string;
  onIntegrityChange: (value: boolean) => void;
  onPublish: () => void;
}

export function CreateProjectPublishSection({
  integrityConfirmed,
  canPublish,
  repoReady,
  isBusy,
  projectSlug,
  onIntegrityChange,
  onPublish,
}: CreateProjectPublishSectionProps) {
  const { t } = useTranslation();

  if (!repoReady) return null;

  return (
    <section
      aria-labelledby="create-publish-title"
      className="flex flex-col gap-6 rounded-2xl border border-border bg-card p-6 shadow-card sm:p-7"
    >
      <div className="border-b border-border pb-4">
        <h2 className="text-base font-bold text-foreground" id="create-publish-title">
          {t("hub.create.sections.publish")}
        </h2>
        <p className="text-xs text-muted-foreground">{t("hub.create.sections.publish_hint")}</p>
      </div>

      <div className="flex items-start gap-3 rounded-xl border border-info/30 bg-info/10 p-4">
        <Globe aria-hidden className="mt-0.5 size-5 shrink-0 text-info" />
        <div className="flex flex-col gap-0.5 text-xs leading-relaxed text-foreground">
          <span className="font-semibold">{t("hub.create.publish.visibility_title")}</span>
          <span className="text-muted-foreground">
            {t("hub.create.publish.visibility_text")}
          </span>
        </div>
      </div>

      <div className="flex items-start gap-3 rounded-xl border border-border bg-secondary/60 p-3.5">
        <Checkbox
          id="create-integrity"
          checked={integrityConfirmed}
          onCheckedChange={(value) => onIntegrityChange(value === true)}
          className="mt-0.5"
        />
        <Label
          htmlFor="create-integrity"
          className="cursor-pointer text-xs font-normal leading-relaxed text-muted-foreground"
        >
          <strong className="font-semibold text-foreground">
            {t("hub.create.publish.integrity_label")}
          </strong>{" "}
          {t("hub.create.publish.integrity_text", { path: projectSlug || "…" })}
        </Label>
      </div>

      <div className="flex justify-end border-t border-border pt-4">
        <Button
          type="button"
          disabled={!canPublish || isBusy}
          onClick={onPublish}
          className="group h-10 w-full gap-2 rounded-lg text-xs font-semibold sm:w-auto"
        >
          {t("hub.create.actions.publish")}
          <ArrowRight
            aria-hidden
            className="size-4 text-brand transition-transform group-hover:translate-x-0.5"
          />
        </Button>
      </div>
    </section>
  );
}
