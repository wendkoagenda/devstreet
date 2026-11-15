import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  BadgeCheck,
  Heart,
  ImageIcon,
  Loader2,
  MessageCircle,
  Sparkles,
  ThumbsUp,
  Video,
  X,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { AI_CHAT } from "@/models/auth/permissions/constants";
import { usePermissions } from "@/hooks/use-permissions";
import { useAuthSlice } from "@/models/auth/slice";
import {
  useAcceptTechnicalReplyMutation,
  useCreatePublicationCommentMutation,
  useGetPublicationCommentsQuery,
  useToggleCommentLikeMutation,
  useToggleConfirmationAideMutation,
  useUploadForumMediaMutation,
} from "../api";
import {
  createCommentSchema,
  type Commentaire,
  type CreateCommentFormValues,
  type CreateCommentInput,
  type MediaCommentaire,
  type OptionPublication,
} from "../schema";
import { ForumAudioPlayer } from "./forum-audio-player";
import { ForumAvatar } from "./forum-avatar";
import { ForumRichText } from "./forum-rich-text";
import { VoiceRecorderButton } from "./voice-recorder-button";

type PendingMedia = {
  url: string;
  kind: "IMAGE" | "VIDEO" | "AUDIO";
  texte_alternatif: string;
  position: number;
};

function CommentMedias({ medias }: { medias?: MediaCommentaire[] }) {
  const { t } = useTranslation();
  if (!medias?.length) return null;
  return (
    <div className="mt-2 space-y-2">
      {medias.map((media) => {
        const src = buildMediaUrl(media.url);
        if (media.kind === "VIDEO") {
          return (
            <video
              key={media.id}
              src={src}
              controls
              preload="metadata"
              className="max-h-72 w-full rounded-xl bg-muted object-contain"
            />
          );
        }
        if (media.kind === "AUDIO") {
          return <ForumAudioPlayer key={media.id} src={src} />;
        }
        return (
          <a
            key={media.id}
            href={src}
            target="_blank"
            rel="noreferrer"
            className="block overflow-hidden rounded-xl bg-muted"
            title={t("forum.comments_open_image")}
          >
            <img
              src={src}
              alt={media.texte_alternatif || t("forum.comments_image")}
              className="max-h-72 w-full object-contain"
              loading="lazy"
            />
          </a>
        );
      })}
    </div>
  );
}

type CommentsSectionProps = {
  publicationId: number;
  publicationType?: string;
  publicationAuthorId?: number | null;
  acceptedReplyId?: number | null;
  allowAnonymousFeedback?: boolean;
  /** Options du débat (pour lier un commentaire à un choix) */
  choixOptions?: OptionPublication[];
  /** Option déjà choisie par l'utilisateur courant */
  defaultOptionId?: number | null;
  /** Chaîne avec commentaires fermés : lecture seule */
  commentsClosed?: boolean;
};

function isSelinaAuthor(comment: Commentaire): boolean {
  const username = comment.auteur?.username?.trim().toLowerCase();
  return username === "selina";
}

function CommentComposer({
  publicationId,
  parentId = null,
  placeholder,
  autoFocus = false,
  allowAnonymous = false,
  technicalReply = false,
  discussionOnly = false,
  choixOptions = [],
  defaultOptionId = null,
  onCancel,
  onSuccess,
}: {
  publicationId: number;
  parentId?: number | null;
  placeholder: string;
  autoFocus?: boolean;
  allowAnonymous?: boolean;
  technicalReply?: boolean;
  /** Commentaire de discussion (pas de médias / pas de solution). */
  discussionOnly?: boolean;
  choixOptions?: OptionPublication[];
  defaultOptionId?: number | null;
  onCancel?: () => void;
  onSuccess?: () => void;
}) {
  const { t } = useTranslation();
  const { hasPermission, isSuperAdmin } = usePermissions();
  const canMentionSelina = isSuperAdmin || hasPermission(AI_CHAT);
  const [createComment, { isLoading: posting }] =
    useCreatePublicationCommentMutation();
  const [uploadMedia, { isLoading: uploading }] =
    useUploadForumMediaMutation();
  const [pendingMedias, setPendingMedias] = useState<PendingMedia[]>([]);
  const [showSelinaSuggest, setShowSelinaSuggest] = useState(false);
  const imageInputRef = useRef<HTMLInputElement | null>(null);
  const videoInputRef = useRef<HTMLInputElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const showChoixSelect = !parentId && choixOptions.length > 0;
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    clearErrors,
    watch,
    formState: { errors },
  } = useForm<CreateCommentFormValues, unknown, CreateCommentInput>({
    resolver: zodResolver(createCommentSchema),
    defaultValues: {
      texte: "",
      parent_id: parentId,
      option_id: showChoixSelect ? defaultOptionId ?? null : null,
      est_anonyme: false,
      nature: "COMMENTAIRE",
      medias_data: [],
    },
  });

  const { ref: texteRef, ...texteRegister } = register("texte");
  const estAnonyme = watch("est_anonyme");
  const texteValue = watch("texte") || "";

  useEffect(() => {
    setValue("medias_data", pendingMedias, { shouldValidate: true });
    if (pendingMedias.length > 0) {
      clearErrors("texte");
    }
  }, [pendingMedias, setValue, clearErrors]);

  useEffect(() => {
    if (!canMentionSelina) {
      setShowSelinaSuggest(false);
      return;
    }
    const typingMention = /(^|\s)@s(e(l(i(n(a)?)?)?)?)?$/i.test(texteValue);
    const alreadyComplete = /(^|\s)@selina\b/i.test(texteValue);
    setShowSelinaSuggest(typingMention && !alreadyComplete);
  }, [canMentionSelina, texteValue]);

  const insertSelinaMention = () => {
    const next = /(^|\s)@s(e(l(i(n(a)?)?)?)?)?$/i.test(texteValue)
      ? texteValue.replace(/(^|\s)@s(e(l(i(n(a)?)?)?)?)?$/i, "$1@selina ")
      : `${texteValue.trimEnd()} @selina `;
    setValue("texte", next, { shouldValidate: true });
    setShowSelinaSuggest(false);
    textareaRef.current?.focus();
  };

  useEffect(() => {
    if (autoFocus) {
      textareaRef.current?.focus();
    }
  }, [autoFocus]);

  const uploadKind = async (
    file: File,
    kind: "IMAGE" | "VIDEO" | "AUDIO"
  ) => {
    if (pendingMedias.length >= 4) {
      toast.error(t("forum.comments_media_max"));
      return;
    }
    const maxBytes =
      kind === "IMAGE"
        ? 5 * 1024 * 1024
        : kind === "VIDEO"
          ? 50 * 1024 * 1024
          : 15 * 1024 * 1024;
    if (file.size > maxBytes) {
      toast.error(
        kind === "IMAGE"
          ? t("forum.comments_image_too_heavy")
          : kind === "VIDEO"
            ? t("forum.comments_video_too_heavy")
            : t("forum.comments_audio_too_heavy")
      );
      return;
    }
    try {
      const uploaded = await uploadMedia({ file, kind }).unwrap();
      setPendingMedias((prev) => [
        ...prev,
        {
          url: uploaded.url,
          kind,
          texte_alternatif: file.name,
          position: prev.length,
        },
      ]);
    } catch {
      toast.error(t("forum.comments_upload_error"));
    }
  };

  const onSubmit = handleSubmit(async (values) => {
    try {
      const anonymous = Boolean(allowAnonymous && !parentId && values.est_anonyme);
      const isAppFeedback = Boolean(allowAnonymous && !parentId);
      const isTechnical = Boolean(technicalReply && !parentId);
      const optionId =
        showChoixSelect && values.option_id ? Number(values.option_id) : null;
      if (showChoixSelect && !optionId) {
        toast.error(t("forum.comments_choice_required"));
        return;
      }
      if (!values.texte?.trim() && pendingMedias.length === 0) {
        toast.error(t("forum.comments_text_or_media"));
        return;
      }
      await createComment({
        publicationId,
        body: {
          texte: values.texte || "",
          parent_id: parentId,
          option_id: optionId,
          est_anonyme: anonymous,
          nature: isTechnical
            ? "REPONSE_TECHNIQUE"
            : isAppFeedback
              ? "RETOUR_APP"
              : "COMMENTAIRE",
          medias_data: pendingMedias,
        },
      }).unwrap();
      reset({
        texte: "",
        parent_id: parentId,
        option_id: showChoixSelect ? defaultOptionId ?? null : null,
        est_anonyme: false,
        medias_data: [],
      });
      setPendingMedias([]);
      toast.success(
        parentId
          ? t("forum.comments_reply_published")
          : anonymous
            ? t("forum.comments_anon_feedback_published")
            : isTechnical
              ? t("forum.comments_technical_published")
              : isAppFeedback
                ? t("forum.comments_feedback_published")
                : t("forum.comments_published")
      );
      onSuccess?.();
    } catch (error: unknown) {
      const apiError =
        error &&
        typeof error === "object" &&
        "data" in error &&
        error.data &&
        typeof error.data === "object" &&
        "error" in error.data
          ? String((error.data as { error: unknown }).error)
          : null;
      toast.error(apiError || t("forum.comments_publish_error"));
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-2">
      {showChoixSelect ? (
        <div className="space-y-1">
          <label
            htmlFor={`comment-option-${publicationId}-${parentId ?? "root"}`}
            className="text-xs font-medium text-muted-foreground"
          >
            {t("forum.comments_choice_label")}
          </label>
          <select
            id={`comment-option-${publicationId}-${parentId ?? "root"}`}
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
            {...register("option_id", {
              setValueAs: (value) =>
                value === "" || value == null ? null : Number(value),
            })}
          >
            <option value="">{t("forum.comments_choice_placeholder")}</option>
            {choixOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.libelle}
              </option>
            ))}
          </select>
        </div>
      ) : null}
      <div className="relative">
        <Textarea
          rows={technicalReply ? 4 : discussionOnly ? 2 : 2}
          placeholder={
            pendingMedias.some((media) => media.kind === "AUDIO")
              ? t("forum.comments_placeholder_voice")
              : placeholder
          }
          className={cn(
            "resize-none",
            technicalReply
              ? "min-h-[96px] border-brand-soft-border bg-background font-mono text-sm"
              : "min-h-[72px]"
          )}
          {...texteRegister}
          onKeyDown={(event) => {
            // Entrée publie ; Maj+Entrée = nouvelle ligne.
            if (event.key !== "Enter" || event.shiftKey) return;
            if (event.nativeEvent.isComposing) return;
            event.preventDefault();
            if (posting || uploading) return;
            void onSubmit();
          }}
          ref={(element) => {
            texteRef(element);
            textareaRef.current = element;
          }}
        />
        {showSelinaSuggest ? (
          <button
            type="button"
            onClick={insertSelinaMention}
            className="absolute bottom-2 left-2 inline-flex items-center gap-1.5 rounded-md border border-brand-soft-border bg-brand-soft px-2 py-1 text-[11px] font-medium text-brand shadow-sm"
          >
            <Sparkles className="size-3" aria-hidden />
            {t("selina.mention_suggest")}
          </button>
        ) : null}
      </div>
      {canMentionSelina && !technicalReply ? (
        <p className="text-[11px] text-muted-foreground">
          {t("selina.mention_hint")}
        </p>
      ) : null}
      {errors.texte ? (
        <p className="text-xs text-destructive">{errors.texte.message}</p>
      ) : null}

      {!discussionOnly && pendingMedias.length > 0 ? (
        <ul className="flex flex-wrap gap-2">
          {pendingMedias.map((media, index) => (
            <li
              key={`${media.url}-${index}`}
              className="relative flex h-16 min-w-16 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted px-2"
            >
              {media.kind === "IMAGE" ? (
                <img
                  src={buildMediaUrl(media.url)}
                  alt=""
                  className="h-full w-16 object-cover"
                />
              ) : media.kind === "VIDEO" ? (
                <span className="text-xs font-medium text-muted-foreground">
                  {t("forum.comments_video")}
                </span>
              ) : (
                <span className="text-xs font-medium text-muted-foreground">
                  {t("forum.comments_audio")}
                </span>
              )}
              <button
                type="button"
                aria-label={t("forum.comments_remove_media")}
                className="absolute right-1 top-1 rounded bg-background/90 p-0.5"
                onClick={() =>
                  setPendingMedias((prev) =>
                    prev.filter((_, i) => i !== index)
                  )
                }
              >
                <X className="h-3 w-3" />
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      {!discussionOnly ? (
        <>
          <input
            ref={imageInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              event.target.value = "";
              if (file) void uploadKind(file, "IMAGE");
            }}
          />
          <input
            ref={videoInputRef}
            type="file"
            accept="video/mp4,video/webm,video/quicktime"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              event.target.value = "";
              if (file) void uploadKind(file, "VIDEO");
            }}
          />
        </>
      ) : null}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1">
          {!discussionOnly ? (
            <>
              <Button
                type="button"
                size="sm"
                variant="ghost"
                className="h-8 gap-1 px-2"
                disabled={uploading || pendingMedias.length >= 4}
                onClick={() => imageInputRef.current?.click()}
              >
                {uploading ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <ImageIcon className="h-3.5 w-3.5" />
                )}
                {t("forum.comments_image")}
              </Button>
              <Button
                type="button"
                size="sm"
                variant="ghost"
                className="h-8 gap-1 px-2"
                disabled={uploading || pendingMedias.length >= 4}
                onClick={() => videoInputRef.current?.click()}
              >
                <Video className="h-3.5 w-3.5" />
                {t("forum.comments_video")}
              </Button>
              <VoiceRecorderButton
                disabled={uploading || pendingMedias.length >= 4}
                confirmLabel={t("forum.comments_attach")}
                onRecorded={(payload) => {
                  setPendingMedias((prev) => [
                    ...prev,
                    {
                      url: payload.url,
                      kind: "AUDIO",
                      texte_alternatif: payload.texte_alternatif,
                      position: prev.length,
                    },
                  ]);
                  toast.success(t("forum.comments_voice_attached"));
                }}
              />
            </>
          ) : (
            <span className="text-xs text-muted-foreground">
              {t("forum.comments_discussion_only")}
            </span>
          )}
          {allowAnonymous && !parentId ? (
            <label className="ml-1 inline-flex items-center gap-2 text-xs text-muted-foreground">
              <input
                type="checkbox"
                className="h-3.5 w-3.5 rounded border-input"
                {...register("est_anonyme")}
              />
              {t("forum.comments_anonymous")}
              {estAnonyme ? (
                <span className="text-muted-foreground/80">
                  {t("forum.comments_anonymous_hint")}
                </span>
              ) : null}
            </label>
          ) : null}
        </div>
        <div className="flex items-center gap-2">
          {onCancel ? (
            <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
              {t("forum.comments_cancel")}
            </Button>
          ) : null}
          <Button
            type="submit"
            size="sm"
            disabled={posting || uploading}
            className={
              technicalReply
                ? "bg-brand text-brand-foreground hover:bg-brand/90"
                : undefined
            }
          >
            {posting
              ? t("forum.comments_sending")
              : technicalReply
                ? t("forum.comments_propose")
                : discussionOnly
                  ? t("forum.comments_comment")
                  : t("forum.comments_publish")}
          </Button>
        </div>
      </div>
    </form>
  );
}

function CommentItem({
  comment,
  publicationId,
  threadRootId,
  replyTo,
  onReply,
  onCancelReply,
  isEntraide,
  isOwner,
  acceptedReplyId,
  commentsClosed = false,
}: {
  comment: Commentaire;
  publicationId: number;
  threadRootId: number;
  replyTo: number | null;
  onReply: (uiCommentId: number) => void;
  onCancelReply: () => void;
  isEntraide: boolean;
  isOwner: boolean;
  acceptedReplyId?: number | null;
  commentsClosed?: boolean;
}) {
  const { t } = useTranslation();
  const [toggleLike, { isLoading }] = useToggleCommentLikeMutation();
  const [toggleAide, { isLoading: confirming }] =
    useToggleConfirmationAideMutation();
  const [acceptReply, { isLoading: accepting }] =
    useAcceptTechnicalReplyMutation();

  const isSelina = isSelinaAuthor(comment);
  const author = comment.est_anonyme
    ? t("forum.comments_anonymous")
    : isSelina
      ? "Selina"
      : comment.auteur?.full_name ||
        comment.auteur?.username ||
        t("forum.member_fallback");
  const isReplying = replyTo === comment.id;
  const isTechnical = comment.nature === "REPONSE_TECHNIQUE";
  const isAccepted = acceptedReplyId === comment.id;

  const handleLike = async () => {
    try {
      await toggleLike({
        commentaireId: comment.id,
        publicationId,
      }).unwrap();
    } catch {
      toast.error(t("forum.comments_like_error"));
    }
  };

  const handleToggleAide = async () => {
    try {
      await toggleAide({
        commentaireId: comment.id,
        publicationId,
      }).unwrap();
    } catch {
      toast.error(t("forum.comments_help_error"));
    }
  };

  const handleAccept = async () => {
    try {
      await acceptReply({
        publicationId,
        commentaireId: isAccepted ? null : comment.id,
      }).unwrap();
      toast.success(
        isAccepted
          ? t("forum.comments_accepted_removed")
          : t("forum.comments_accepted")
      );
    } catch {
      toast.error(t("forum.comments_accept_error"));
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-3">
        <ForumAvatar
          name={author}
          photo={comment.est_anonyme ? null : comment.auteur?.photo}
          size="sm"
          tone="muted"
          className="mt-0.5"
        />
        <div className="min-w-0 flex-1 space-y-2">
          <div
            className={cn(
              "rounded-xl px-3 py-2",
              isSelina
                ? "border border-brand-soft-border bg-brand-soft/60"
                : isTechnical
                  ? "border border-brand-soft-border bg-background"
                  : "bg-muted/50",
              isAccepted && "border-brand bg-brand-soft/50 ring-1 ring-brand/20"
            )}
          >
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-sm font-semibold text-foreground">{author}</p>
              {isSelina ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-brand-soft-border bg-card px-2 py-0.5 text-[10px] font-semibold text-brand">
                  <Sparkles className="h-3 w-3" aria-hidden />
                  {t("selina.mention_badge")}
                </span>
              ) : null}
              {isTechnical ? (
                <span className="rounded-full border border-brand-soft-border bg-brand-soft px-2 py-0.5 text-[10px] font-semibold text-brand">
                  {t("forum.comments_technical_badge")}
                </span>
              ) : null}
              {comment.est_anonyme || comment.nature === "RETOUR_APP" ? (
                <span className="rounded-full border border-border bg-background px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                  {comment.est_anonyme
                    ? t("forum.comments_anon_feedback_badge")
                    : t("forum.comments_app_feedback_badge")}
                </span>
              ) : null}
              {isAccepted ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-brand-soft-border bg-brand-soft px-2 py-0.5 text-[10px] font-medium text-brand-strong">
                  <BadgeCheck className="h-3 w-3" />
                  {t("forum.comments_accepted_badge")}
                </span>
              ) : null}
              {comment.option_libelle ? (
                <span className="rounded-full border border-brand-soft-border bg-brand-soft/50 px-2 py-0.5 text-[10px] font-medium text-brand-strong">
                  {t("forum.comments_on_option", {
                    label: comment.option_libelle,
                  })}
                </span>
              ) : null}
            </div>
            {comment.texte?.trim() ? (
              <ForumRichText
                text={comment.texte}
                compact
                className={cn(
                  "mt-1 text-foreground/90",
                  isTechnical && "text-[13px]"
                )}
              />
            ) : null}
            <CommentMedias medias={comment.medias} />
          </div>
          <div className="flex flex-wrap items-center gap-3 pl-1 text-xs text-muted-foreground">
            {!isSelina ? (
              <button
                type="button"
                disabled={isLoading}
                onClick={handleLike}
                aria-label={
                  comment.liked_by_me
                    ? t("forum.comments_unlike")
                    : t("forum.comments_like")
                }
                aria-pressed={comment.liked_by_me}
                className={cn(
                  "inline-flex items-center gap-1 hover:text-foreground",
                  comment.liked_by_me && "text-destructive"
                )}
              >
                <Heart
                  className={cn(
                    "h-3.5 w-3.5",
                    comment.liked_by_me && "fill-current"
                  )}
                />
                {comment.likes_count}
              </button>
            ) : null}
            {!commentsClosed && !isSelina ? (
              <button
                type="button"
                onClick={() => onReply(comment.id)}
                aria-label={t("forum.comments_reply_to", { name: author })}
                aria-expanded={isReplying}
                className={cn(
                  "hover:text-foreground",
                  isReplying && "font-medium text-foreground"
                )}
              >
                {t("forum.comments_reply")}
              </button>
            ) : null}
            {isEntraide && isTechnical ? (
              <button
                type="button"
                disabled={confirming}
                onClick={handleToggleAide}
                aria-label={
                  comment.confirmed_by_me
                    ? t("forum.comments_helped_undo")
                    : t("forum.comments_helped")
                }
                aria-pressed={comment.confirmed_by_me}
                className={cn(
                  "inline-flex items-center gap-1 hover:text-foreground",
                  comment.confirmed_by_me && "font-medium text-foreground"
                )}
              >
                <ThumbsUp
                  className={cn(
                    "h-3.5 w-3.5",
                    comment.confirmed_by_me && "fill-current"
                  )}
                />
                {t("forum.comments_helped")}
                {(comment.confirmations_count ?? 0) > 0
                  ? ` · ${comment.confirmations_count}`
                  : ""}
              </button>
            ) : null}
            {isEntraide && isTechnical && isOwner ? (
              <button
                type="button"
                disabled={accepting}
                onClick={handleAccept}
                className="hover:text-foreground"
              >
                {isAccepted
                  ? t("forum.comments_unaccept")
                  : t("forum.comments_accept")}
              </button>
            ) : null}
          </div>

          {isReplying && !commentsClosed ? (
            <div className="pt-1">
              <CommentComposer
                publicationId={publicationId}
                parentId={threadRootId}
                placeholder={t("forum.comments_reply_placeholder", {
                  name: author,
                })}
                autoFocus
                onCancel={onCancelReply}
                onSuccess={onCancelReply}
              />
            </div>
          ) : null}
        </div>
      </div>

      {comment.reponses?.length ? (
        <div className="ml-8 space-y-3 border-l border-border pl-4">
          {comment.reponses.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={{ ...reply, reponses: [] }}
              publicationId={publicationId}
              threadRootId={threadRootId}
              replyTo={replyTo}
              onReply={onReply}
              onCancelReply={onCancelReply}
              isEntraide={isEntraide}
              isOwner={isOwner}
              acceptedReplyId={acceptedReplyId}
              commentsClosed={commentsClosed}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function CommentsSection({
  publicationId,
  publicationType,
  publicationAuthorId,
  acceptedReplyId = null,
  allowAnonymousFeedback = false,
  choixOptions = [],
  defaultOptionId = null,
  commentsClosed = false,
}: CommentsSectionProps) {
  const { t } = useTranslation();
  const currentUserId = useAuthSlice((state) => state.user?.id);
  const { data, isLoading, isError, refetch } =
    useGetPublicationCommentsQuery(publicationId);
  const [replyTo, setReplyTo] = useState<number | null>(null);

  const isEntraide = publicationType === "ENTRAIDE";
  const isChoix = publicationType === "CHOIX";
  const isOwner = Boolean(
    currentUserId && publicationAuthorId && currentUserId === publicationAuthorId
  );

  const technicalReplies =
    data?.filter((comment) => comment.nature === "REPONSE_TECHNIQUE") ?? [];
  const rootComments =
    data?.filter((comment) => comment.nature !== "REPONSE_TECHNIQUE") ?? [];

  // Entraide : uniquement des réponses techniques (les précisions se font en fil sous une solution).
  if (isEntraide) {
    return (
      <section className="space-y-4 rounded-2xl border border-brand-soft-border bg-brand-soft/30 p-4 shadow-sm sm:p-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <BadgeCheck className="h-4 w-4 text-brand" />
            <h2 className="text-base font-semibold text-foreground">
              {t("forum.comments_technical_title")}
            </h2>
          </div>
          <p className="text-xs leading-relaxed text-muted-foreground">
            {t("forum.comments_technical_hint")}
          </p>
        </div>

        {commentsClosed ? (
          <p className="rounded-xl border border-border bg-muted/40 px-3 py-2 text-sm text-muted-foreground">
            {t("forum.comments_replies_closed")}
          </p>
        ) : (
          <CommentComposer
            publicationId={publicationId}
            placeholder={t("forum.comments_placeholder_technical")}
            technicalReply
          />
        )}

        {isLoading ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            {t("forum.loading")}
          </p>
        ) : null}

        {isError ? (
          <div className="space-y-2 py-4 text-center">
            <p className="text-sm text-destructive">
              {t("forum.comments_replies_load_error")}
            </p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => refetch()}
            >
              {t("forum.comments_retry")}
            </Button>
          </div>
        ) : null}

        {!isLoading && !isError && technicalReplies.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            {t("forum.comments_technical_empty")}
          </p>
        ) : null}

        <div className="space-y-5">
          {technicalReplies.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              publicationId={publicationId}
              threadRootId={comment.id}
              replyTo={replyTo}
              onReply={setReplyTo}
              onCancelReply={() => setReplyTo(null)}
              isEntraide
              isOwner={isOwner}
              acceptedReplyId={acceptedReplyId}
              commentsClosed={commentsClosed}
            />
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-4 rounded-2xl border border-border bg-card p-4 shadow-sm sm:p-5">
      <div className="flex items-center gap-2">
        <MessageCircle className="h-4 w-4 text-muted-foreground" />
        <h2 className="text-base font-semibold text-foreground">
          {allowAnonymousFeedback
            ? t("forum.comments_feedback_title")
            : t("forum.comments_title")}
        </h2>
      </div>

      {commentsClosed ? (
        <p className="rounded-xl border border-border bg-muted/40 px-3 py-2 text-sm text-muted-foreground">
          {t("forum.comments_closed_channel")}
        </p>
      ) : (
        <CommentComposer
          publicationId={publicationId}
          placeholder={
            allowAnonymousFeedback
              ? t("forum.comments_placeholder_feedback")
              : isChoix
                ? t("forum.comments_placeholder_choice")
                : t("forum.comments_placeholder")
          }
          allowAnonymous={allowAnonymousFeedback}
          choixOptions={isChoix ? choixOptions : []}
          defaultOptionId={isChoix ? defaultOptionId : null}
        />
      )}

      {isLoading ? (
        <p className="py-6 text-center text-sm text-muted-foreground">
          {t("forum.comments_loading")}
        </p>
      ) : null}

      {isError ? (
        <div className="space-y-2 py-6 text-center">
          <p className="text-sm text-destructive">
            {t("forum.comments_load_error")}
          </p>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => refetch()}
          >
            {t("forum.comments_retry")}
          </Button>
        </div>
      ) : null}

      {!isLoading && !isError && rootComments.length === 0 ? (
        <p className="py-6 text-center text-sm text-muted-foreground">
          {allowAnonymousFeedback
            ? t("forum.comments_feedback_empty")
            : t("forum.comments_empty")}
        </p>
      ) : null}

      <div className="space-y-5">
        {rootComments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            publicationId={publicationId}
            threadRootId={comment.id}
            replyTo={replyTo}
            onReply={setReplyTo}
            onCancelReply={() => setReplyTo(null)}
            isEntraide={false}
            isOwner={isOwner}
            acceptedReplyId={acceptedReplyId}
            commentsClosed={commentsClosed}
          />
        ))}
      </div>
    </section>
  );
}
