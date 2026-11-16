import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { SelinaMascotte } from "@/models/ai/components/selina-mascotte";

type LocalTurn = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

/**
 * Mini-hôte Selina pour la landing guest.
 * Chat 100 % local : aucune requête `/api/v1/ai/*`.
 */
export function LandingSelinaHost() {
  const { t } = useTranslation();
  const [draft, setDraft] = useState("");
  const [turns, setTurns] = useState<LocalTurn[]>([]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const message = draft.trim();
    if (!message) return;

    const userTurn: LocalTurn = {
      id: `u-${Date.now()}`,
      role: "user",
      content: message,
    };
    const reply: LocalTurn = {
      id: `a-${Date.now()}`,
      role: "assistant",
      content: t("selina.landing_gate_reply"),
    };
    setTurns((prev) => [...prev, userTurn, reply]);
    setDraft("");
  };

  return (
    <section
      className="mx-auto w-full max-w-xl px-4 sm:px-6"
      aria-label={t("selina.title")}
    >
      <div className="flex flex-col items-center gap-4 text-center">
        <SelinaMascotte size="lg" interactive ariaLabel={t("selina.mascotte_aria")} />
        <p className="max-w-md rounded-2xl border border-border/70 bg-card/90 px-4 py-3 text-sm leading-relaxed text-foreground shadow-sm">
          {t("selina.landing_welcome")}
        </p>
      </div>

      {turns.length > 0 ? (
        <div className="mt-5 max-h-56 space-y-3 overflow-y-auto rounded-2xl border border-border/60 bg-card/70 p-3 text-left scrollbar-none">
          {turns.map((turn) => (
            <div
              key={turn.id}
              className={cn(
                "text-sm leading-relaxed",
                turn.role === "user" ? "text-right" : "text-left"
              )}
            >
              <span
                className={cn(
                  "inline-block max-w-[90%] rounded-2xl px-3.5 py-2",
                  turn.role === "user"
                    ? "bg-muted text-foreground"
                    : "bg-brand-soft/60 text-foreground"
                )}
              >
                {turn.content}
              </span>
              {turn.role === "assistant" ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button asChild size="sm" className="rounded-full">
                    <Link to="/login">{t("selina.landing_login_cta")}</Link>
                  </Button>
                  <Button asChild size="sm" variant="outline" className="rounded-full">
                    <Link to="/login?mode=register">
                      {t("selina.landing_register_cta")}
                    </Link>
                  </Button>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      ) : null}

      <form
        className="mt-4 flex items-center gap-2 rounded-full border border-border/80 bg-card/95 px-3 py-1.5 shadow-sm"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={t("selina.landing_prompt_placeholder")}
          aria-label={t("selina.landing_prompt_placeholder")}
          className="min-w-0 flex-1 border-0 bg-transparent px-2 py-2 text-sm outline-none placeholder:text-muted-foreground"
        />
        <button
          type="submit"
          disabled={!draft.trim()}
          className={cn(
            "inline-flex size-9 shrink-0 items-center justify-center rounded-full transition-colors",
            draft.trim()
              ? "bg-foreground text-background hover:bg-foreground/90"
              : "bg-muted text-muted-foreground"
          )}
          aria-label={t("selina.send")}
        >
          <ArrowUp className="size-4" strokeWidth={2.25} aria-hidden />
        </button>
      </form>
    </section>
  );
}
