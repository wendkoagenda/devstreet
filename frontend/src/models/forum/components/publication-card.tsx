import { useEffect, useState, type KeyboardEvent, type MouseEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Code2,
  Expand,
  ExternalLink,
  FolderKanban,
  Heart,
  HelpCircle,
  MessageCircle,
  MessagesSquare,
  Share2,
  Sparkles,
  UserPlus,
  Users,
  Vote,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import {
  useQuitterEspaceMutation,
  useRejoindreEspaceMutation,
  useTogglePublicationFavoriMutation,
  useTogglePublicationLikeMutation,
  useToggleSuivreMembreMutation,
} from "../api";
import type { Publication, PublicationImage } from "../schema";
import { ChoixOptionsButtons } from "./choix-options-buttons";
import { FeedVideoPlayer } from "./feed-video-player";
import { ForumAvatar } from "./forum-avatar";
import { ForumRichText } from "./forum-rich-text";

type PublicationCardProps = {
  publication: Publication;
  showFullBody?: boolean;
  /** Désactive la navigation au clic (page détail). */
  disableCardNav?: boolean;
};

const TYPE_META: Record<
  Publication["type"],
  {
    label: string;
    Icon: typeof MessagesSquare;
    soft: string;
  }
> = {
  DISCUSSION: {
    label: "Discussion",
    Icon: MessagesSquare,
    soft: "bg-info/10 text-info",
  },
  APPLICATION: {
    label: "Showcase",
    Icon: Sparkles,
    soft: "bg-brand-soft text-brand-strong",
  },
  ENTRAIDE: {
    label: "Code Review",
    Icon: Code2,
    soft: "bg-warning-soft text-warning",
  },
  CHOIX: {
    label: "Débat",
    Icon: HelpCircle,
    soft: "bg-success/10 text-success",
  },
  SONDAGE: {
    label: "Sondage",
    Icon: Vote,
    soft: "bg-brand-soft text-brand-strong",
  },
};

const PLATEFORME_LABELS: Record<"WEB" | "MOBILE" | "LES_DEUX", string> = {
  WEB: "Web",
  MOBILE: "Mobile",
  LES_DEUX: "Web & mobile",
};

function safeHttpUrl(value: string | undefined | null): string | null {
  const url = (value ?? "").trim();
  return /^https?:\/\//i.test(url) ? url : null;
}

function formatRelativeDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const diffMs = Date.now() - date.getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "à l'instant";
  if (minutes < 60) return `il y a ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `il y a ${hours} h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `il y a ${days} j`;
  return new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(date);
}

function MediaTile({
  media,
  titre,
  className,
  fit = "cover",
  autoplay = false,
}: {
  media: PublicationImage;
  titre: string;
  className?: string;
  fit?: "cover" | "contain";
  autoplay?: boolean;
}) {
  const objectClass = fit === "contain" ? "object-contain" : "object-cover";
  if (media.kind === "VIDEO") {
    if (autoplay) {
      return (
        <FeedVideoPlayer
          src={media.url}
          label={media.texte_alternatif || titre}
          className={className}
        />
      );
    }
    return (
      <video
        src={`${buildMediaUrl(media.url)}#t=0.1`}
        muted
        playsInline
        preload="metadata"
        className={cn("bg-muted", objectClass, className)}
        aria-label={media.texte_alternatif || titre}
      />
    );
  }
  return (
    <img
      src={buildMediaUrl(media.url)}
      alt={media.texte_alternatif || titre}
      className={cn(objectClass, className)}
      loading="lazy"
    />
  );
}

function MediaLightbox({
  images,
  titre,
  index,
  open,
  onOpenChange,
}: {
  images: PublicationImage[];
  titre: string;
  index: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [current, setCurrent] = useState(index);
  const media = images[current];

  useEffect(() => {
    if (open) setCurrent(index);
  }, [open, index]);

  useEffect(() => {
    if (!open || images.length < 2) return;
    const onKey = (event: globalThis.KeyboardEvent) => {
      if (event.key === "ArrowRight") {
        setCurrent((value) => (value + 1) % images.length);
      } else if (event.key === "ArrowLeft") {
        setCurrent((value) => (value - 1 + images.length) % images.length);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, images.length]);

  if (!media) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-h-[95dvh] w-[min(100vw-1rem,72rem)] max-w-none border-none bg-transparent p-0 shadow-none sm:rounded-none [&>button:last-child]:hidden"
        aria-describedby={undefined}
      >
        <DialogTitle className="sr-only">{titre || "Média"}</DialogTitle>
        <div className="relative flex min-h-[50dvh] items-center justify-center">
          <DialogClose asChild>
            <Button
              type="button"
              size="icon"
              variant="secondary"
              className="absolute right-2 top-2 z-10 size-9 rounded-full bg-background/90"
              aria-label="Fermer"
            >
              <X className="size-4" />
            </Button>
          </DialogClose>

          {images.length > 1 ? (
            <>
              <Button
                type="button"
                size="icon"
                variant="secondary"
                className="absolute left-2 z-10 size-9 rounded-full bg-background/90"
                aria-label="Média précédent"
                onClick={() =>
                  setCurrent((value) => (value - 1 + images.length) % images.length)
                }
              >
                <ChevronLeft className="size-4" />
              </Button>
              <Button
                type="button"
                size="icon"
                variant="secondary"
                className="absolute right-12 top-2 z-10 size-9 rounded-full bg-background/90 sm:right-14"
                aria-label="Média suivant"
                onClick={() =>
                  setCurrent((value) => (value + 1) % images.length)
                }
              >
                <ChevronRight className="size-4" />
              </Button>
            </>
          ) : null}

          <div className="flex max-h-[90dvh] w-full items-center justify-center rounded-xl bg-black/40 p-2 sm:p-4">
            {media.kind === "VIDEO" ? (
              <video
                key={media.id}
                src={buildMediaUrl(media.url)}
                controls
                autoPlay
                playsInline
                className="max-h-[85dvh] max-w-full rounded-lg object-contain"
                aria-label={media.texte_alternatif || titre}
              />
            ) : (
              <img
                key={media.id}
                src={buildMediaUrl(media.url)}
                alt={media.texte_alternatif || titre}
                className="max-h-[85dvh] max-w-full rounded-lg object-contain"
              />
            )}
          </div>

          {images.length > 1 ? (
            <p className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-full bg-background/90 px-3 py-1 text-xs text-muted-foreground">
              {current + 1} / {images.length}
            </p>
          ) : null}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function MediaMosaic({
  images,
  titre,
}: {
  images: PublicationImage[];
  titre: string;
}) {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  if (images.length === 0) return null;

  const openAt = (index: number) => setLightboxIndex(index);

  if (images.length === 1) {
    const cover = images[0];
    if (cover.kind === "VIDEO") {
      return (
        <FeedVideoPlayer
          src={cover.url}
          label={cover.texte_alternatif || titre}
        />
      );
    }
    return (
      <>
        <button
          type="button"
          onClick={() => openAt(0)}
          className="group/media relative block w-full overflow-hidden rounded-xl bg-muted text-left"
          aria-label="Agrandir l'image"
        >
          <MediaTile
            media={cover}
            titre={titre}
            fit="contain"
            className="max-h-[28rem] w-full transition duration-500 ease-out group-hover/media:scale-[1.01]"
          />
          <span className="absolute bottom-2 right-2 inline-flex items-center gap-1 rounded-full bg-background/90 px-2 py-1 text-[11px] font-medium text-muted-foreground opacity-0 shadow-sm transition group-hover/media:opacity-100 group-focus-visible/media:opacity-100">
            <Expand className="size-3" aria-hidden />
            Voir en grand
          </span>
        </button>
        <MediaLightbox
          images={images}
          titre={titre}
          index={0}
          open={lightboxIndex != null}
          onOpenChange={(open) => setLightboxIndex(open ? 0 : null)}
        />
      </>
    );
  }

  if (images.length === 2) {
    return (
      <>
        <div className="grid grid-cols-2 gap-1 overflow-hidden rounded-xl">
          {images.slice(0, 2).map((image, index) => (
            <button
              key={image.id}
              type="button"
              onClick={() => openAt(index)}
              className="relative block overflow-hidden bg-muted text-left"
              aria-label={`Agrandir le média ${index + 1}`}
            >
              <MediaTile
                media={image}
                titre={titre}
                className="h-44 w-full sm:h-52"
              />
            </button>
          ))}
        </div>
        <MediaLightbox
          images={images}
          titre={titre}
          index={lightboxIndex ?? 0}
          open={lightboxIndex != null}
          onOpenChange={(open) =>
            setLightboxIndex(open ? lightboxIndex ?? 0 : null)
          }
        />
      </>
    );
  }

  const rest = images.length - 3;
  return (
    <>
      <div className="grid grid-cols-2 gap-1 overflow-hidden rounded-xl">
        <button
          type="button"
          onClick={() => openAt(0)}
          className="relative block overflow-hidden bg-muted text-left"
          aria-label="Agrandir le média 1"
        >
          <MediaTile
            media={images[0]}
            titre={titre}
            className="row-span-2 h-full min-h-[11rem] w-full sm:min-h-[14rem]"
          />
        </button>
        <button
          type="button"
          onClick={() => openAt(1)}
          className="relative block overflow-hidden bg-muted text-left"
          aria-label="Agrandir le média 2"
        >
          <MediaTile
            media={images[1]}
            titre={titre}
            className="h-[5.5rem] w-full sm:h-28"
          />
        </button>
        <button
          type="button"
          onClick={() => openAt(2)}
          className="relative block overflow-hidden bg-muted text-left"
          aria-label={
            rest > 0 ? `Voir ${rest + 1} médias de plus` : "Agrandir le média 3"
          }
        >
          <MediaTile
            media={images[2]}
            titre={titre}
            className="h-[5.5rem] w-full sm:h-28"
          />
          {rest > 0 ? (
            <span className="absolute inset-0 flex items-center justify-center bg-foreground/55 text-sm font-semibold text-background">
              +{rest}
            </span>
          ) : null}
        </button>
      </div>
      <MediaLightbox
        images={images}
        titre={titre}
        index={lightboxIndex ?? 0}
        open={lightboxIndex != null}
        onOpenChange={(open) =>
          setLightboxIndex(open ? lightboxIndex ?? 0 : null)
        }
      />
    </>
  );
}

function FollowPublicationTarget({
  publication,
}: {
  publication: Publication;
}) {
  const currentUserId = useAuthSlice((state) => state.user?.id ?? null);
  const [toggleSuivre, { isLoading: followBusy }] =
    useToggleSuivreMembreMutation();
  const [rejoindre, { isLoading: joinBusy }] = useRejoindreEspaceMutation();
  const [quitter, { isLoading: leaveBusy }] = useQuitterEspaceMutation();
  const [following, setFollowing] = useState(
    Boolean(publication.following_auteur)
  );
  const [joined, setJoined] = useState(
    Boolean(publication.espace?.joined_by_me)
  );

  useEffect(() => {
    setFollowing(Boolean(publication.following_auteur));
    setJoined(Boolean(publication.espace?.joined_by_me));
  }, [
    publication.id,
    publication.following_auteur,
    publication.espace?.joined_by_me,
  ]);

  const auteurId = publication.auteur?.id;
  const isOwn = auteurId != null && auteurId === currentUserId;
  const channelPublic =
    publication.espace?.type === "CHAINE" &&
    (publication.espace.acces ?? "PUBLIC") === "PUBLIC";
  const isolated = !publication.espace?.id;
  const busy = followBusy || joinBusy || leaveBusy;

  if (channelPublic && publication.espace?.id) {
    const handleToggleChannel = async () => {
      const espaceId = publication.espace!.id;
      const prev = joined;
      setJoined(!prev);
      try {
        if (prev) {
          await quitter(espaceId).unwrap();
          toast.success("Tu t'es désabonné de la chaîne");
        } else {
          await rejoindre(espaceId).unwrap();
          toast.success("Tu suis cette chaîne");
        }
      } catch {
        setJoined(prev);
        toast.error(
          prev
            ? "Impossible de se désabonner"
            : "Impossible de s'abonner à la chaîne"
        );
      }
    };

    return (
      <Button
        type="button"
        size="sm"
        variant={joined ? "outline" : "default"}
        className="h-8 shrink-0 gap-1.5"
        disabled={busy}
        onClick={() => void handleToggleChannel()}
      >
        <Users className="h-3.5 w-3.5" aria-hidden />
        {joined ? "Abonné" : "Suivre la chaîne"}
      </Button>
    );
  }

  if (isolated && auteurId && !isOwn) {
    const handleToggleAuthor = async () => {
      const prev = following;
      setFollowing(!prev);
      try {
        const result = await toggleSuivre(auteurId).unwrap();
        setFollowing(result.following);
        toast.success(
          result.following
            ? "Tu suis ce membre"
            : "Tu ne suis plus ce membre"
        );
      } catch {
        setFollowing(prev);
        toast.error("Impossible de mettre à jour le suivi");
      }
    };

    return (
      <Button
        type="button"
        size="sm"
        variant={following ? "outline" : "default"}
        className="h-8 shrink-0 gap-1.5"
        disabled={busy}
        onClick={() => void handleToggleAuthor()}
      >
        <UserPlus className="h-3.5 w-3.5" aria-hidden />
        {following ? "Suivi" : "Suivre"}
      </Button>
    );
  }

  return null;
}

function isInteractiveTarget(target: EventTarget | null) {
  if (!(target instanceof Element)) return false;
  return Boolean(
    target.closest(
      "a, button, input, textarea, select, label, [role='button'], [data-no-card-nav]"
    )
  );
}

export function PublicationCard({
  publication,
  showFullBody = false,
  disableCardNav = false,
}: PublicationCardProps) {
  const navigate = useNavigate();
  const [toggleLike] = useTogglePublicationLikeMutation();
  const [toggleFavori] = useTogglePublicationFavoriMutation();
  const [liked, setLiked] = useState(Boolean(publication.liked_by_me));
  const [likesCount, setLikesCount] = useState(publication.likes_count ?? 0);
  const [saved, setSaved] = useState(Boolean(publication.saved_by_me));
  const [likeBusy, setLikeBusy] = useState(false);
  const [saveBusy, setSaveBusy] = useState(false);
  const [likePulse, setLikePulse] = useState(false);

  useEffect(() => {
    setLiked(Boolean(publication.liked_by_me));
    setLikesCount(publication.likes_count ?? 0);
    setSaved(Boolean(publication.saved_by_me));
  }, [
    publication.id,
    publication.liked_by_me,
    publication.likes_count,
    publication.saved_by_me,
  ]);

  const authorName =
    publication.auteur?.full_name ||
    publication.auteur?.username ||
    "Membre";
  const handle = publication.auteur?.username
    ? `@${publication.auteur.username}`
    : "@membre";
  const typeMeta = TYPE_META[publication.type];
  const TypeIcon = typeMeta.Icon;
  const body =
    !showFullBody && publication.description.length > 280
      ? `${publication.description.slice(0, 280).trim()}…`
      : publication.description;
  const isApplication = publication.type === "APPLICATION";
  const demoUrl = safeHttpUrl(publication.lien_app);
  const plateformeKey = publication.plateforme_app as
    | keyof typeof PLATEFORME_LABELS
    | "";
  const detailHref = `/forum/publications/${publication.id}`;
  const publicationUrl = `${window.location.origin}${detailHref}`;
  const commentsCount = publication.comments_count ?? 0;

  const openPublication = () => {
    navigate(detailHref);
  };

  const handleCardClick = (event: MouseEvent<HTMLElement>) => {
    if (disableCardNav) return;
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (isInteractiveTarget(event.target)) return;
    openPublication();
  };

  const handleCardKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (disableCardNav) return;
    if (event.key !== "Enter" && event.key !== " ") return;
    if (isInteractiveTarget(event.target)) return;
    event.preventDefault();
    openPublication();
  };

  const handleToggleLike = () => {
    if (likeBusy) return;
    const prevLiked = liked;
    const prevCount = likesCount;
    const nextLiked = !prevLiked;
    setLiked(nextLiked);
    setLikesCount(Math.max(0, prevCount + (nextLiked ? 1 : -1)));
    if (nextLiked) {
      setLikePulse(true);
      window.setTimeout(() => setLikePulse(false), 420);
    }
    setLikeBusy(true);
    void toggleLike(publication.id)
      .unwrap()
      .catch(() => {
        setLiked(prevLiked);
        setLikesCount(prevCount);
        toast.error("Impossible de mettre à jour le like");
      })
      .finally(() => setLikeBusy(false));
  };

  const handleShare = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: publication.titre,
          text: publication.titre,
          url: publicationUrl,
        });
        return;
      }
      await navigator.clipboard.writeText(publicationUrl);
      toast.success("Lien copié");
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        return;
      }
      try {
        await navigator.clipboard.writeText(publicationUrl);
        toast.success("Lien copié");
      } catch {
        toast.error("Impossible de partager");
      }
    }
  };

  const handleToggleFavori = () => {
    if (saveBusy) return;
    const prevSaved = saved;
    const nextSaved = !prevSaved;
    setSaved(nextSaved);
    setSaveBusy(true);
    void toggleFavori(publication.id)
      .unwrap()
      .catch(() => {
        setSaved(prevSaved);
        toast.error("Impossible de mettre à jour le favori");
      })
      .finally(() => setSaveBusy(false));
  };

  const authorBlock = (
    <div className="flex items-center gap-3">
      {publication.auteur?.id ? (
        <Link
          to={`/forum/profil/${publication.auteur.id}`}
          className="shrink-0"
          aria-label={`Profil de ${authorName}`}
        >
          <ForumAvatar
            name={authorName}
            photo={publication.auteur?.photo}
            tone="soft"
            size={isApplication ? "sm" : "md"}
          />
        </Link>
      ) : (
        <ForumAvatar
          name={authorName}
          photo={publication.auteur?.photo}
          tone="soft"
          size={isApplication ? "sm" : "md"}
        />
      )}
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
          {publication.auteur?.id ? (
            <Link
              to={`/forum/profil/${publication.auteur.id}`}
              className="truncate text-sm font-semibold text-foreground hover:underline"
            >
              {authorName}
            </Link>
          ) : (
            <span className="truncate text-sm font-semibold text-foreground">
              {authorName}
            </span>
          )}
          <span className="truncate text-xs text-muted-foreground">
            {handle}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          {formatRelativeDate(publication.created_at)}
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        <span
          className={cn(
            "inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] font-medium",
            typeMeta.soft
          )}
        >
          <TypeIcon className="h-3 w-3" aria-hidden />
          {typeMeta.label}
        </span>
        <FollowPublicationTarget publication={publication} />
      </div>
    </div>
  );

  const contextLinks =
    publication.espace?.id || publication.projet?.id ? (
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
        {publication.espace?.id ? (
          <Link
            to={
              publication.espace.type === "CHAINE"
                ? `/forum/chaines/${publication.espace.id}`
                : `/forum/communautes/${publication.espace.id}`
            }
            className="inline-flex max-w-full items-center gap-1 font-medium text-muted-foreground transition-colors hover:text-brand"
          >
            <Users className="h-3.5 w-3.5 shrink-0" aria-hidden />
            <span className="truncate">{publication.espace.nom}</span>
          </Link>
        ) : null}
        {publication.projet?.id ? (
          <Link
            to={`/hub/projects/${publication.projet.id}`}
            className="inline-flex max-w-full items-center gap-1 font-medium text-muted-foreground transition-colors hover:text-brand"
          >
            <FolderKanban className="h-3.5 w-3.5 shrink-0" aria-hidden />
            <span className="truncate">
              {publication.projet.titre?.trim() ||
                `Projet #${publication.projet.id}`}
            </span>
          </Link>
        ) : null}
      </div>
    ) : null;

  return (
    <article
      role={disableCardNav ? undefined : "link"}
      tabIndex={disableCardNav ? undefined : 0}
      aria-label={
        disableCardNav
          ? undefined
          : `Ouvrir la publication : ${publication.titre}`
      }
      onClick={handleCardClick}
      onKeyDown={handleCardKeyDown}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-border bg-card transition duration-300",
        "hover:border-border/80 hover:shadow-[0_12px_40px_-24px_hsl(var(--foreground)/0.35)]",
        !disableCardNav &&
          "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40"
      )}
    >
      {isApplication && publication.images.length > 0 ? (
        <div className="relative" data-no-card-nav>
          <MediaMosaic
            images={publication.images}
            titre={publication.titre}
          />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-card via-card/70 to-transparent" />
        </div>
      ) : null}

      <div className="space-y-3 p-4 sm:p-5">
        {authorBlock}
        {contextLinks}

        <div className="space-y-2.5">
          <h2
            className={cn(
              "font-semibold tracking-tight text-foreground",
              isApplication
                ? "text-xl sm:text-2xl"
                : "text-lg leading-snug sm:text-xl"
            )}
          >
            <Link
              to={detailHref}
              className="transition-colors hover:text-brand"
            >
              {publication.titre}
            </Link>
          </h2>

          <div
            className={cn(
              "text-sm leading-relaxed text-muted-foreground",
              isApplication && "line-clamp-3"
            )}
          >
            <ForumRichText text={body} />
          </div>
        </div>

        {!isApplication ? (
          <div data-no-card-nav>
            <MediaMosaic
              images={publication.images}
              titre={publication.titre}
            />
          </div>
        ) : null}

        {isApplication ? (
          <div className="flex flex-wrap items-center gap-2 pt-0.5">
            {plateformeKey && plateformeKey in PLATEFORME_LABELS ? (
              <span className="rounded-md border border-border bg-muted/80 px-2 py-1 text-xs font-medium text-foreground">
                {PLATEFORME_LABELS[plateformeKey]}
              </span>
            ) : null}
            {demoUrl ? (
              <Button
                asChild
                size="sm"
                className="gap-2 bg-brand text-brand-foreground hover:bg-brand/90"
              >
                <a href={demoUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-3.5 w-3.5" />
                  Tester la démo
                </a>
              </Button>
            ) : null}
          </div>
        ) : null}

        {publication.type === "CHOIX" ? (
          <ChoixOptionsButtons
            publication={publication}
            showDescriptions={showFullBody}
          />
        ) : null}

        {publication.type === "CHOIX" &&
        publication.decided_at &&
        publication.justification_finale ? (
          <p className="border-l-2 border-success pl-3 text-sm text-foreground/90">
            <span className="font-medium text-success">Décision — </span>
            {publication.justification_finale}
          </p>
        ) : null}

        <div className="flex items-center justify-between gap-2 border-t border-border/80 pt-3">
          <div className="flex items-center gap-0.5">
            <button
              type="button"
              disabled={likeBusy}
              onClick={handleToggleLike}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm transition-colors",
                "hover:bg-muted",
                liked
                  ? "text-destructive"
                  : "text-muted-foreground hover:text-foreground"
              )}
              aria-label={liked ? "Retirer le like" : "Liker"}
              aria-pressed={liked}
              title={liked ? "Retirer le like" : "Liker"}
            >
              <Heart
                className={cn(
                  "h-4 w-4 transition-transform",
                  liked && "fill-current",
                  likePulse && "scale-125"
                )}
              />
              <span className="tabular-nums">{likesCount}</span>
            </button>
            <Link
              to={detailHref}
              className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              aria-label={`${commentsCount} commentaire${commentsCount > 1 ? "s" : ""}`}
            >
              <MessageCircle className="h-4 w-4" />
              <span className="tabular-nums">{commentsCount}</span>
              <span className="hidden text-xs sm:inline">
                {commentsCount > 1 ? "réponses" : "répondre"}
              </span>
            </Link>
          </div>
          <div className="flex items-center gap-0.5">
            <button
              type="button"
              onClick={() => void handleShare()}
              className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              aria-label="Partager"
              title="Partager"
            >
              <Share2 className="h-4 w-4" />
            </button>
            <button
              type="button"
              disabled={saveBusy}
              onClick={handleToggleFavori}
              className={cn(
                "rounded-lg p-2 transition-colors hover:bg-muted",
                saved
                  ? "text-brand"
                  : "text-muted-foreground hover:text-foreground"
              )}
              aria-label={
                saved ? "Retirer des favoris" : "Ajouter aux favoris"
              }
              aria-pressed={saved}
              title={saved ? "Retirer des favoris" : "Ajouter aux favoris"}
            >
              <Bookmark
                className={cn("h-4 w-4", saved && "fill-current")}
              />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
