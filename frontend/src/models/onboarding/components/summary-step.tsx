import { Check, Circle } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { completionPercent, type CompletionItem } from "../completion";
import { OnboardingShell } from "./onboarding-shell";

/** Dernier écran : niveau de complétion et liens vers les formulaires complets. */
export function SummaryStep({
  items,
  onFinish,
}: {
  items: CompletionItem[];
  onFinish: () => void;
}) {
  const percent = completionPercent(items);

  return (
    <OnboardingShell
      title="Votre espace est prêt"
      description="Vous pouvez compléter votre profil à tout moment depuis les formulaires complets."
    >
      <div className="mb-5">
        <div className="mb-1.5 flex items-baseline justify-between text-sm">
          <span className="font-medium text-foreground">Profil complété</span>
          <span className="font-mono text-foreground">{percent} %</span>
        </div>
        <div
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Profil complété"
          className="h-2 overflow-hidden rounded-full bg-muted"
        >
          <div className="h-full rounded-full bg-brand transition-all" style={{ width: `${percent}%` }} />
        </div>
      </div>

      <ul className="flex flex-col gap-2">
        {items.map((item) => (
          <li key={item.id} className="flex items-center gap-2.5 text-sm">
            {item.done ? (
              <Check className="size-4 shrink-0 text-brand-strong" aria-hidden />
            ) : (
              <Circle className="size-4 shrink-0 text-muted-foreground" aria-hidden />
            )}
            <span className={item.done ? "text-foreground" : "text-muted-foreground"}>{item.label}</span>
            {!item.done ? (
              <Link
                to={item.href}
                className="ml-auto text-[13px] font-medium text-brand-strong underline-offset-4 hover:underline"
              >
                Compléter
              </Link>
            ) : null}
          </li>
        ))}
      </ul>

      <Button type="button" className="mt-6 w-full" onClick={onFinish}>
        Accéder à mon espace
      </Button>
    </OnboardingShell>
  );
}
