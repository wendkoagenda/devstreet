import { useEffect, useRef, useState, type PointerEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, Check, Info, Undo2, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { profilePath } from "@/helpers/routes/profile-path";
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
  /** Compteur à côté de la position (« Vivier : 2 »…) ; sans cette fonction, aucun compteur n'est affiché. */
  keptLabel?: (kept: number) => string;
  /** Masque l'en-tête (titre, position, compteur) et la phrase d'instruction : seules les cartes restent. */
  hideHeader?: boolean;
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
  hideHeader = false,
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
      {hideHeader ? null : (
        <>
          <div className="flex w-full max-w-md flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-1.5">
              <h1 className="text-xl font-semibold text-foreground">{title}</h1>
              {/* Mode d'emploi dans une bulle : s'ouvre au clic sur le « i » */}
              <Popover>
                <PopoverTrigger asChild>
                  <Button type="button" variant="ghost" size="icon" className="size-7 rounded-full text-muted-foreground" aria-label="Comment ça marche ?">
                    <Info className="size-4" aria-hidden />
                  </Button>
                </PopoverTrigger>
                <PopoverContent align="start" className="w-72 text-xs leading-relaxed">
                  Glissez la carte vers la droite pour {likeVerb}, vers la gauche pour passer, ou utilisez les boutons.
                </PopoverContent>
              </Popover>
            </div>
            <div className="flex gap-2">
              {keptLabel ? <Badge>{keptLabel(kept)}</Badge> : null}
            </div>
          </div>
        </>
      )}

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
              <ProfileInitialsAvatar
                name={card.name}
                size="xl"
                kind={card.type === "entreprise" ? "entreprise" : "dev"}
                openToWork={card.type !== "entreprise" && card.is_open_to_work}
              />
              <div className="flex min-w-0 flex-col gap-0.5">
                {card.type ? (
                  <Badge
                    variant="outline"
                    className={`w-fit ${
                      card.type === "entreprise"
                        ? "border-brand bg-brand-soft text-brand-strong"
                        : "border-border text-muted-foreground"
                    }`}
                  >
                    {card.type === "entreprise" ? "Entreprise" : "Dev"}
                  </Badge>
                ) : null}
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
            <div className="mt-auto flex items-center justify-between gap-3">
              <span className="text-xs text-muted-foreground">{facts.source}</span>
              {card.username ? (
                <Button asChild size="sm" variant="outline" className="shrink-0">
                  <Link
                    to={profilePath(card.username, card.type === "entreprise" ? "entreprise" : "dev")}
                    // Ne pas démarrer un glissement de la carte quand on clique sur le lien
                    onPointerDown={(event) => event.stopPropagation()}
                  >
                    Voir le profil
                    <ArrowUpRight className="ml-1 size-3.5" aria-hidden />
                  </Link>
                </Button>
              ) : null}
            </div>
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
            <span className="text-2xl font-semibold">Vous êtes connectés !</span>
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
