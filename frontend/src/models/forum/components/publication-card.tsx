import { useEffect, useState, type KeyboardEvent, type MouseEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Code2,
  Expand,
  ExternalLink,
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
  useToggleSuivreTagMutation,
} from "../api";
import type { ForumTag, Publication, PublicationImage } from "../schema";
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
  }
> = {
  DISCUSSION: {
    label: "Discussion",
    Icon: MessagesSquare,
  },
  APPLICATION: {
    label: "Showcase",
    Icon: Sparkles,
  },
  ENTRAIDE: {
    label: "Code Review",
    Icon: Code2,
  },
  CHOIX: {
    label: "Débat",
    Icon: HelpCircle,
  },
  SONDAGE: {
    label: "Sondage",
    Icon: Vote,
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
    const isCreator = publication.espace.mon_role === "SUPER_ADMIN";

    if (isCreator) {
      return (
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="h-7 shrink-0 gap-1 px-2 text-[11px] sm:h-8 sm:gap-1.5 sm:px-3 sm:text-sm"
          disabled
          title="Tu es le créateur de cette chaîne"
        >
          <Users className="h-3 w-3 sm:h-3.5 sm:w-3.5" aria-hidden />
          Créateur
        </Button>
      );
    }

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
      } catch (error) {
        setJoined(prev);
        const apiError =
          error &&
          typeof error === "object" &&
          "data" in error &&
          error.data &&
          typeof error.data === "object" &&
          "error" in error.data
            ? String((error.data as { error: unknown }).error)
            : null;
        toast.error(
          apiError ||
            (prev
              ? "Impossible de se désabonner"
              : "Impossible de s'abonner à la chaîne")
        );
      }
    };

    return (
      <Button
        type="button"
        size="sm"
        variant={joined ? "outline" : "default"}
        className="h-7 shrink-0 gap-1 px-2 text-[11px] sm:h-8 sm:gap-1.5 sm:px-3 sm:text-sm"
        disabled={busy}
        onClick={() => void handleToggleChannel()}
      >
        <Users className="h-3 w-3 sm:h-3.5 sm:w-3.5" aria-hidden />
        {joined ? "Abonné" : "Suivre"}
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
        className="h-7 shrink-0 gap-1 px-2 text-[11px] sm:h-8 sm:gap-1.5 sm:px-3 sm:text-sm"
        disabled={busy}
        onClick={() => void handleToggleAuthor()}
      >
        <UserPlus className="h-3 w-3 sm:h-3.5 sm:w-3.5" aria-hidden />
        {following ? "Suivi" : "Suivre"}
      </Button>
    );
  }

  return null;
}

function PublicationTagChip({ tag }: { tag: ForumTag }) {
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const [toggleSuivreTag, { isLoading }] = useToggleSuivreTagMutation();
  const [followed, setFollowed] = useState(Boolean(tag.followed_by_me));

  useEffect(() => {
    setFollowed(Boolean(tag.followed_by_me));
  }, [tag.id, tag.followed_by_me]);

  const handleToggleFollow = async () => {
    if (!isAuthenticated || isLoading) return;
    const prev = followed;
    setFollowed(!prev);
    try {
      const result = await toggleSuivreTag(tag.slug).unwrap();
      setFollowed(result.following);
      toast.success(
        result.following
          ? `#${tag.slug} ajouté à Mes favoris`
          : `#${tag.slug} retiré de Mes favoris`
      );
    } catch {
      setFollowed(prev);
      toast.error("Impossible de mettre à jour le thème");
    }
  };

  return (
    <button
      type="button"
      disabled={!isAuthenticated || isLoading}
      onClick={() => void handleToggleFollow()}
      className={cn(
        "rounded-md border px-2 py-0.5 font-mono text-[11px] transition-colors",
        followed
          ? "border-brand-soft-border bg-brand-soft text-brand"
          : "border-border bg-muted/40 text-muted-foreground hover:border-brand-soft-border hover:bg-brand-soft hover:text-brand"
      )}
      aria-label={
        followed ? `Ne plus suivre #${tag.slug}` : `Suivre #${tag.slug}`
      }
      aria-pressed={followed}
      title={followed ? "Dans Tags suivis" : "Ajouter aux tags suivis"}
    >
      #{tag.slug}
    </button>
  );
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

  const contextSubtitle =
    publication.espace?.nom ||
    (publication.projet?.titre?.trim()
      ? publication.projet.titre.trim()
      : publication.projet?.id
        ? `Projet #${publication.projet.id}`
        : null);

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
        "overflow-hidden rounded-lg border border-border bg-card",
        !disableCardNav &&
          "cursor-pointer transition-shadow hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30"
      )}
    >
      <div className="flex items-start gap-2.5 px-3 pt-3 sm:gap-3 sm:px-5 sm:pt-5">
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
              size="sm"
              className="sm:h-10 sm:w-10 sm:text-xs"
            />
          </Link>
        ) : (
          <ForumAvatar
            name={authorName}
            photo={publication.auteur?.photo}
            tone="soft"
            size="sm"
            className="sm:h-10 sm:w-10 sm:text-xs"
          />
        )}

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-x-1.5 gap-y-0.5">
                {publication.auteur?.id ? (
                  <Link
                    to={`/forum/profil/${publication.auteur.id}`}
                    className="truncate text-[13px] font-semibold text-foreground hover:text-brand hover:underline sm:text-sm"
                  >
                    {authorName}
                  </Link>
                ) : (
                  <span className="truncate text-[13px] font-semibold text-foreground sm:text-sm">
                    {authorName}
                  </span>
                )}
                <span className="text-muted-foreground">·</span>
                <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground sm:text-xs">
                  <TypeIcon className="size-3" aria-hidden />
                  {typeMeta.label}
                </span>
              </div>
              <p className="mt-0.5 truncate text-[11px] text-muted-foreground sm:text-xs">
                {handle}
                {contextSubtitle ? (
                  <>
                    <span aria-hidden> · </span>
                    {publication.espace?.id ? (
                      <Link
                        to={
                          publication.espace.type === "CHAINE"
                            ? `/forum/chaines/${publication.espace.id}`
                            : `/forum/communautes/${publication.espace.id}`
                        }
                        className="hover:text-brand hover:underline"
                      >
                        {contextSubtitle}
                      </Link>
                    ) : publication.projet?.id ? (
                      <Link
                        to={`/hub/projects/${publication.projet.id}`}
                        className="hover:text-brand hover:underline"
                      >
                        {contextSubtitle}
                      </Link>
                    ) : (
                      contextSubtitle
                    )}
                  </>
                ) : null}
                <span aria-hidden> · </span>
                <time dateTime={publication.created_at}>
                  {formatRelativeDate(publication.created_at)}
                </time>
              </p>
            </div>
            <div className="shrink-0" data-no-card-nav>
              <FollowPublicationTarget publication={publication} />
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-2 px-3 pt-2.5 sm:space-y-3 sm:px-5 sm:pt-3">
        <div className="space-y-1 sm:space-y-1.5">
          <h2 className="text-[14px] font-semibold leading-snug text-foreground sm:text-[15px] md:text-base">
            <Link to={detailHref} className="hover:text-brand hover:underline">
              {publication.titre}
            </Link>
          </h2>
          <div
            className={cn(
              "text-[13px] leading-relaxed text-foreground/90 sm:text-sm",
              isApplication && !showFullBody && "line-clamp-3"
            )}
          >
            <ForumRichText
              text={body}
              className="text-[13px] text-foreground/90 sm:text-sm"
            />
          </div>
          {(publication.tags?.length ?? 0) > 0 ? (
            <div className="flex flex-wrap gap-1.5 pt-1" data-no-card-nav>
              {publication.tags.map((tag) => (
                <PublicationTagChip key={tag.id} tag={tag} />
              ))}
            </div>
          ) : null}
        </div>

        {isApplication ? (
          <div className="flex flex-wrap items-center gap-2" data-no-card-nav>
            {plateformeKey && plateformeKey in PLATEFORME_LABELS ? (
              <span className="rounded-md bg-muted px-2 py-1 text-[11px] font-medium text-muted-foreground">
                {PLATEFORME_LABELS[plateformeKey]}
              </span>
            ) : null}
            {demoUrl ? (
              <Button
                asChild
                size="sm"
                variant="outline"
                className="h-8 gap-1.5"
              >
                <a href={demoUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="size-3.5" />
                  Tester la démo
                </a>
              </Button>
            ) : null}
          </div>
        ) : null}

        {publication.type === "CHOIX" ? (
          <div data-no-card-nav>
            <ChoixOptionsButtons
              publication={publication}
              showDescriptions={showFullBody}
            />
          </div>
        ) : null}

        {publication.type === "CHOIX" &&
        publication.decided_at &&
        publication.justification_finale ? (
          <p className="rounded-md bg-muted/60 px-3 py-2 text-sm text-foreground/90">
            <span className="font-medium text-success">Décision — </span>
            {publication.justification_finale}
          </p>
        ) : null}
      </div>

      {publication.images.length > 0 ? (
        <div className="mt-3" data-no-card-nav>
          <MediaMosaic images={publication.images} titre={publication.titre} />
        </div>
      ) : null}

      {(likesCount > 0 || commentsCount > 0) ? (
        <div className="mt-2 flex items-center justify-between gap-2 px-3 text-[11px] text-muted-foreground sm:px-5 sm:text-xs">
          <span className="tabular-nums">
            {likesCount > 0
              ? `${likesCount} j'aime${likesCount > 1 ? "s" : ""}`
              : ""}
          </span>
          {commentsCount > 0 ? (
            <Link to={detailHref} className="hover:text-brand hover:underline">
              {commentsCount} commentaire{commentsCount > 1 ? "s" : ""}
            </Link>
          ) : (
            <span />
          )}
        </div>
      ) : null}

      <div
        className="mt-1 grid grid-cols-4 border-t border-border/80"
        data-no-card-nav
      >
        <button
          type="button"
          disabled={likeBusy}
          onClick={handleToggleLike}
          className={cn(
            "inline-flex items-center justify-center gap-1 py-2 text-xs font-medium transition-colors hover:bg-muted sm:gap-1.5 sm:py-2.5 sm:text-sm",
            liked ? "text-destructive" : "text-muted-foreground"
          )}
          aria-label={liked ? "Retirer le like" : "J'aime"}
          aria-pressed={liked}
        >
          <Heart
            className={cn(
              "size-3.5 sm:size-4",
              liked && "fill-current",
              likePulse && "scale-110"
            )}
          />
          <span className="hidden sm:inline">J&apos;aime</span>
        </button>
        <Link
          to={detailHref}
          className="inline-flex items-center justify-center gap-1 py-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted sm:gap-1.5 sm:py-2.5 sm:text-sm"
        >
          <MessageCircle className="size-3.5 sm:size-4" />
          <span className="hidden sm:inline">Commenter</span>
        </Link>
        <button
          type="button"
          onClick={() => void handleShare()}
          className="inline-flex items-center justify-center gap-1 py-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted sm:gap-1.5 sm:py-2.5 sm:text-sm"
          aria-label="Partager"
        >
          <Share2 className="size-3.5 sm:size-4" />
          <span className="hidden sm:inline">Partager</span>
        </button>
        <button
          type="button"
          disabled={saveBusy}
          onClick={handleToggleFavori}
          className={cn(
            "inline-flex items-center justify-center gap-1 py-2 text-xs font-medium transition-colors hover:bg-muted sm:gap-1.5 sm:py-2.5 sm:text-sm",
            saved ? "text-brand" : "text-muted-foreground"
          )}
          aria-label={saved ? "Retirer des favoris" : "Enregistrer"}
          aria-pressed={saved}
        >
          <Bookmark className={cn("size-3.5 sm:size-4", saved && "fill-current")} />
          <span className="hidden sm:inline">Enregistrer</span>
        </button>
      </div>
    </article>
  );
}
