import { useEffect, useRef, useState, type PointerEvent, type ReactNode } from "react";
import { Check, Undo2, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { initialsOf } from "@/models/marketplace-offers/labels";
import type { DeckCard, SwipeResult } from "../schema";

/** Distance de glissement (px) à partir de laquelle un relâchement vaut un choix. */
const DECIDE_DISTANCE = 110;
const EXIT_DISTANCE = 720;
const EXIT_MS = 260;

export type CardFacts = {
  k1: string;
  v1: string;
  k2: string;
  v2: string;
  proof: string;
  source: string;
};

type SwipeDeckProps = {
  cards: DeckCard[];
  title: string;
  /** « garder le profil dans votre vivier », « proposer de devenir amis »… */
  likeVerb: string;
  likeStamp: string;
  likeAria: string;
  keptLabel: (kept: number) => string;
  emptyAction: ReactNode;
  matchedText: (name: string) => string;
  matchedAction?: ReactNode;
  describe: (card: DeckCard) => CardFacts;
  /** Enregistre le choix ; retourne null si l'enregistrement a échoué (la carte reste alors affichée). */
  onSwipe: (card: DeckCard, direction: "like" | "pass") => Promise<SwipeResult | null>;
  /** Annule le dernier choix côté serveur ; retourne false en cas d'échec. */
  onUndo: () => Promise<boolean>;
};

/** Paquet de cartes à glisser (droite : garder, gauche : passer) ou à décider avec les boutons. */
export function SwipeDeck({
  cards,
  title,
  likeVerb,
  likeStamp,
  likeAria,
  keptLabel,
  emptyAction,
  matchedText,
  matchedAction,
  describe,
  onSwipe,
  onUndo,
}: SwipeDeckProps) {
  const [index, setIndex] = useState(0);
  const [kept, setKept] = useState(0);
  const [history, setHistory] = useState<number[]>([]);
  const [dx, setDx] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [matched, setMatched] = useState("");
  const busy = useRef(false);
  const startX = useRef<number | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const card = index < cards.length ? cards[index] : null;
  const rotation = dx / 18;

  const decide = (direction: 1 | -1) => {
    if (busy.current || !card || matched) return;
    busy.current = true;
    setDragging(false);
    setDx(direction * EXIT_DISTANCE);
    window.setTimeout(async () => {
      const result = await onSwipe(card, direction > 0 ? "like" : "pass");
      if (!mounted.current) return;
      if (result) {
        setHistory((items) => [...items, direction]);
        if (direction > 0) setKept((count) => count + 1);
        setIndex((value) => value + 1);
        if (result.matched) setMatched(result.profil.name);
      }
      // la carte suivante apparaît sans animation de retour
      setDragging(true);
      setDx(0);
      window.setTimeout(() => {
        if (!mounted.current) return;
        setDragging(false);
        busy.current = false;
      }, 40);
    }, EXIT_MS);
  };

  const undo = async () => {
    if (busy.current || history.length === 0) return;
    busy.current = true;
    const ok = await onUndo();
    if (mounted.current && ok) {
      const last = history[history.length - 1];
      setHistory((items) => items.slice(0, -1));
      setIndex((value) => Math.max(0, value - 1));
      if (last > 0) setKept((count) => Math.max(0, count - 1));
      setMatched("");
    }
    busy.current = false;
  };

  const onPointerDown = (event: PointerEvent<HTMLElement>) => {
    if (busy.current) return;
    startX.current = event.clientX;
    // suit le doigt ou la souris même hors de la carte (absent de certains environnements de test)
    event.currentTarget.setPointerCapture?.(event.pointerId);
    setDragging(true);
  };
  const onPointerMove = (event: PointerEvent<HTMLElement>) => {
    if (startX.current === null) return;
    setDx(event.clientX - startX.current);
  };
  const onPointerUp = () => {
    if (startX.current === null) return;
    startX.current = null;
    if (dx > DECIDE_DISTANCE) decide(1);
    else if (dx < -DECIDE_DISTANCE) decide(-1);
    else {
      setDx(0);
      setDragging(false);
    }
  };

  const facts = card ? describe(card) : null;
  const hasBack1 = card !== null && index + 1 < cards.length;
  const hasBack2 = card !== null && index + 2 < cards.length;

  return (
    <section aria-label={title} className="flex flex-col items-center gap-4">
      <div className="flex w-full max-w-md flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold text-foreground">{title}</h1>
        <div className="flex gap-2">
          <Badge variant="outline">
            {Math.min(index + 1, cards.length)} / {cards.length}
          </Badge>
          <Badge>{keptLabel(kept)}</Badge>
        </div>
      </div>
      <p className="max-w-md text-center text-xs text-muted-foreground">
        Glissez la carte vers la droite pour {likeVerb}, vers la gauche pour passer, ou utilisez
        les boutons.
      </p>

      <div className="relative h-[26rem] w-full max-w-md">
        {hasBack2 ? (
          <div
            aria-hidden
            className="absolute inset-0 translate-y-5 scale-90 rounded-xl border border-border bg-card opacity-50"
          />
        ) : null}
        {hasBack1 ? (
          <div
            aria-hidden
            className="absolute inset-0 translate-y-2.5 scale-95 rounded-xl border border-border bg-card opacity-80"
          />
        ) : null}

        {card && facts && !matched ? (
          <article
            className={`absolute inset-0 flex cursor-grab touch-none select-none flex-col gap-4 rounded-xl border border-border bg-card p-6 shadow-sm active:cursor-grabbing ${
              dragging ? "" : "transition-transform duration-[260ms] motion-reduce:transition-none"
            }`}
            style={{ transform: `translateX(${dx}px) rotate(${rotation}deg)` }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={onPointerUp}
          >
            {dx > 50 ? (
              <span className="absolute right-4 top-4 rotate-[10deg] rounded-md border-2 border-primary px-2.5 py-1 text-sm font-bold text-primary">
                {likeStamp}
              </span>
            ) : null}
            {dx < -50 ? (
              <span className="absolute right-4 top-4 rotate-[10deg] rounded-md border-2 border-muted-foreground px-2.5 py-1 text-sm font-bold text-muted-foreground">
                Passer
              </span>
            ) : null}

            <div className="flex items-center gap-3">
              <span
                className="flex size-16 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-lg font-semibold text-foreground"
                aria-hidden
              >
                {initialsOf(card.name)}
              </span>
              <div className="flex min-w-0 flex-col gap-0.5">
                <span className="truncate text-lg font-semibold text-foreground">{card.name}</span>
                <span className="text-xs text-muted-foreground">
                  {[card.headline, card.city].filter(Boolean).join(" · ")}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {card.skills.map((skill) => (
                <Badge key={skill} variant="outline">
                  {skill}
                </Badge>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              <div className="rounded-lg border border-border bg-muted/40 p-2.5">
                <span className="text-xs text-muted-foreground">{facts.k1}</span>
                <div className="text-sm font-semibold text-foreground">{facts.v1}</div>
              </div>
              <div className="rounded-lg border border-border bg-muted/40 p-2.5">
                <span className="text-xs text-muted-foreground">{facts.k2}</span>
                <div className="text-sm font-semibold text-foreground">{facts.v2}</div>
              </div>
            </div>

            <p className="text-xs leading-relaxed text-muted-foreground">{facts.proof}</p>
            <span className="mt-auto text-xs text-muted-foreground">{facts.source}</span>
          </article>
        ) : null}

        {!card && !matched ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-xl border border-border bg-card p-6 text-center">
            <span className="text-sm font-semibold text-foreground">
              Plus de profils pour le moment
            </span>
            <span className="text-xs text-muted-foreground">
              Revenez plus tard pour de nouvelles recommandations.
            </span>
            {emptyAction}
          </div>
        ) : null}

        {matched ? (
          <div
            role="status"
            className="absolute inset-0 flex flex-col items-center justify-center gap-4 rounded-xl bg-primary p-6 text-center text-primary-foreground"
          >
            <span className="text-2xl font-semibold">Vous êtes amis !</span>
            <span className="text-sm opacity-90">{matchedText(matched)}</span>
            <div className="flex flex-wrap justify-center gap-2">
              <Button variant="secondary" onClick={() => setMatched("")}>
                Continuer à découvrir
              </Button>
              {matchedAction}
            </div>
          </div>
        ) : null}
      </div>

      <div className="flex items-center gap-4">
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="size-12 rounded-full"
          aria-label="Annuler le dernier choix"
          disabled={history.length === 0}
          onClick={undo}
        >
          <Undo2 className="size-5" />
        </Button>
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="size-14 rounded-full"
          aria-label="Passer"
          disabled={!card || Boolean(matched)}
          onClick={() => decide(-1)}
        >
          <X className="size-6" />
        </Button>
        <Button
          type="button"
          size="icon"
          className="size-14 rounded-full"
          aria-label={likeAria}
          disabled={!card || Boolean(matched)}
          onClick={() => decide(1)}
        >
          <Check className="size-6" />
        </Button>
      </div>
    </section>
  );
}
