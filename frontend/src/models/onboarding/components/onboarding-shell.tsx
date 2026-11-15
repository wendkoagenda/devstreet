import type { ReactNode } from "react";
import { BrandLogo } from "@/components/brand/brand-logo";
import { cn } from "@/lib/utils";

/** Cadre plein écran de l'assistant : logo, progression, titre et contenu de l'étape. */
export function OnboardingShell({
  title,
  description,
  stepIndex,
  stepCount,
  children,
}: {
  title: string;
  description?: string;
  /** Position de l'étape (0 = première) ; absente = pas de progression affichée. */
  stepIndex?: number;
  stepCount?: number;
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-svh flex-col items-center bg-background px-4 py-8 sm:py-12">
      <div className="mb-8">
        <BrandLogo className="h-9" />
      </div>

      <main className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8">
        {stepIndex != null && stepCount != null && stepCount > 1 ? (
          <ol
            aria-label="Progression"
            className="mb-6 flex items-center gap-2"
          >
            {Array.from({ length: stepCount }, (_, index) => (
              <li
                key={index}
                aria-current={index === stepIndex ? "step" : undefined}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-colors",
                  index <= stepIndex ? "bg-brand" : "bg-muted"
                )}
              />
            ))}
          </ol>
        ) : null}

        <h1 className="text-xl font-semibold text-foreground">{title}</h1>
        {description ? (
          <p className="mt-1.5 mb-6 text-sm text-muted-foreground">{description}</p>
        ) : (
          <div className="mb-6" />
        )}

        {children}
      </main>
    </div>
  );
}
