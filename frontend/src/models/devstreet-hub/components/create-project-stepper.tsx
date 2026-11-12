import { Check } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { ProgressStep } from "../hooks/use-create-project";

interface CreateProjectStepperProps {
  progressStep: ProgressStep;
  setupFailed: boolean;
}

const ORDER: ProgressStep[] = ["form", "draft", "identity", "repository", "init", "done"];

function rank(step: ProgressStep): number {
  return ORDER.indexOf(step);
}

export function CreateProjectStepper({
  progressStep,
  setupFailed,
}: CreateProjectStepperProps) {
  const { t } = useTranslation();
  const current = rank(progressStep);

  const steps: { id: ProgressStep; labelKey: string }[] = [
    { id: "draft", labelKey: "hub.create.progress.draft" },
    { id: "identity", labelKey: "hub.create.progress.identity" },
    { id: "repository", labelKey: "hub.create.progress.repository" },
    { id: "init", labelKey: "hub.create.progress.init" },
  ];

  return (
    <div className="w-full rounded-2xl border border-border bg-card p-4 shadow-card sm:p-6">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map((step, index) => {
          const stepRank = rank(step.id);
          const done = current > stepRank || progressStep === "done";
          const active = progressStep === step.id || (progressStep === "form" && index === 0);
          const failed =
            setupFailed &&
            (step.id === "identity" || step.id === "repository") &&
            (progressStep === step.id || progressStep === "identity" || progressStep === "repository");

          return (
            <div
              key={step.id}
              className={cn(
                "flex items-center gap-3 rounded-xl border p-3",
                active && !failed && "border-brand/30 bg-brand-soft/40 ring-2 ring-brand/15",
                failed && "border-destructive/40 bg-destructive/5",
                done && !active && "border-border bg-secondary",
                !active && !done && !failed && "border-border/70 bg-secondary/60 opacity-80"
              )}
            >
              <div
                className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold",
                  failed && "bg-destructive text-destructive-foreground",
                  active && !failed && "bg-brand text-brand-foreground",
                  done && !active && "bg-primary text-primary-foreground",
                  !active && !done && !failed && "bg-muted text-muted-foreground"
                )}
              >
                {done && !failed ? (
                  <Check aria-hidden className="size-4 text-success" />
                ) : (
                  String(index + 1).padStart(2, "0")
                )}
              </div>
              <span className="truncate text-sm font-semibold text-foreground">
                {t(step.labelKey)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
