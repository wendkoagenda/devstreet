import { useEffect, useRef, useState } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AppWindow,
  AtSign,
  ImageIcon,
  LifeBuoy,
  Loader2,
  MessageSquareText,
  Scale,
  SendHorizontal,
  Video,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import {
  createApplicationSchema,
  createChoixSchema,
  createDiscussionSchema,
  createEntraideSchema,
  type CreateApplicationInput,
  type CreateChoixInput,
  type CreateDiscussionInput,
} from "../schema";
import {
  useCreateApplicationMutation,
  useCreateChoixMutation,
  useCreateDiscussionMutation,
  useCreateEntraideMutation,
  useLazySearchMembresQuery,
  useUploadForumImageMutation,
  useUploadForumMediaMutation,
} from "../api";
import { ForumAvatar } from "./forum-avatar";

const IMAGE_ACCEPT = "image/jpeg,image/png,image/gif,image/webp";
const VIDEO_ACCEPT = "video/mp4,video/webm,video/quicktime";
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const MAX_VIDEO_BYTES = 50 * 1024 * 1024;

type FeedComposerProps = {
  onCreated?: (id: number) => void;
  espaceId?: number | null;
  discussionOnly?: boolean;
};

type ComposerMode =
  | "DISCUSSION"
  | "APPLICATION"
  | "ENTRAIDE"
  | "CHOIX";

type ComposerValues = CreateDiscussionInput &
  Partial<Pick<CreateApplicationInput, "lien_app" | "plateforme_app">> &
  Partial<Pick<CreateChoixInput, "contraintes" | "options_data">>;

function schemaForMode(mode: ComposerMode) {
  if (mode === "APPLICATION") return createApplicationSchema;
  if (mode === "ENTRAIDE") return createEntraideSchema;
  if (mode === "CHOIX") return createChoixSchema;
  return createDiscussionSchema;
}

type ComposerFormProps = {
  mode: ComposerMode;
  onModeChange: (mode: ComposerMode) => void;
  onCreated?: (id: number) => void;
  onCancel: () => void;
  espaceId?: number | null;
  discussionOnly?: boolean;
};

function ComposerForm({
  mode,
  onModeChange,
  onCreated,
  onCancel,
  espaceId = null,
  discussionOnly = false,
}: ComposerFormProps) {
  const publicationImageInputRef = useRef<HTMLInputElement | null>(null);
  const publicationVideoInputRef = useRef<HTMLInputElement | null>(null);
  const optionImageInputRef = useRef<HTMLInputElement | null>(null);
  const descriptionRef = useRef<HTMLTextAreaElement | null>(null);
  const [optionImageTarget, setOptionImageTarget] = useState<number | null>(
    null
  );
  const [mentionOpen, setMentionOpen] = useState(false);
  const [mentionQuery, setMentionQuery] = useState("");
  const [searchMembres, { data: mentionResults = [], isFetching: searchingMembres }] =
    useLazySearchMembresQuery();
  const [uploadForumImage, { isLoading: uploadingImage }] =
    useUploadForumImageMutation();
  const [uploadForumMedia, { isLoading: uploadingVideo }] =
    useUploadForumMediaMutation();
  const [createDiscussion, { isLoading: creatingDiscussion }] =
    useCreateDiscussionMutation();
  const [createApplication, { isLoading: creatingApplication }] =
    useCreateApplicationMutation();
  const [createEntraide, { isLoading: creatingEntraide }] =
    useCreateEntraideMutation();
  const [createChoix, { isLoading: creatingChoix }] = useCreateChoixMutation();
  const isLoading =
    uploadingImage ||
    uploadingVideo ||
    creatingDiscussion ||
    creatingApplication ||
    creatingEntraide ||
    creatingChoix;

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    getValues,
    watch,
    formState: { errors },
  } = useForm<ComposerValues>({
    // Remonté via key={mode} dans le parent pour recharger le resolver
    resolver: zodResolver(schemaForMode(mode)) as Resolver<ComposerValues>,
    defaultValues: {
      titre: "",
      description: "",
      images_data: [],
      lien_app: "",
      plateforme_app: "WEB",
      contraintes: "",
      options_data: [
        { libelle: "", description: "", image_url: "", position: 0 },
        { libelle: "", description: "", image_url: "", position: 1 },
      ],
    },
  });

  const descriptionRegister = register("description");
  const images = watch("images_data") ?? [];
  const optionsData = watch("options_data") ?? [];

  useEffect(() => {
    if (!mentionOpen) return;
    const q = mentionQuery.trim();
    if (q.length < 1) return;
    const handle = window.setTimeout(() => {
      void searchMembres(q);
    }, 200);
    return () => window.clearTimeout(handle);
  }, [mentionOpen, mentionQuery, searchMembres]);

  const insertMention = (username: string) => {
    const textarea = descriptionRef.current;
    const current = getValues("description") || "";
    const mention = `@${username} `;
    if (!textarea) {
      setValue("description", `${current}${mention}`, {
        shouldDirty: true,
        shouldValidate: true,
      });
    } else {
      const start = textarea.selectionStart ?? current.length;
      const end = textarea.selectionEnd ?? current.length;
      const next = `${current.slice(0, start)}${mention}${current.slice(end)}`;
      setValue("description", next, {
        shouldDirty: true,
        shouldValidate: true,
      });
      window.requestAnimationFrame(() => {
        const caret = start + mention.length;
        textarea.focus();
        textarea.setSelectionRange(caret, caret);
      });
    }
    setMentionOpen(false);
    setMentionQuery("");
  };

  const resetForm = () => {
    reset({
      titre: "",
      description: "",
      images_data: [],
      lien_app: "",
      plateforme_app: "WEB",
      contraintes: "",
      options_data: [
        { libelle: "", description: "", image_url: "", position: 0 },
        { libelle: "", description: "", image_url: "", position: 1 },
      ],
    });
    setOptionImageTarget(null);
  };

  const uploadImageFile = async (file: File): Promise<string | null> => {
    if (!file.type.startsWith("image/")) {
      toast.error("Choisis une image (jpg, png, gif, webp)");
      return null;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      toast.error("Image trop lourde (max 5 Mo)");
      return null;
    }
    try {
      const uploaded = await uploadForumImage(file).unwrap();
      return uploaded.url;
    } catch {
      toast.error("Impossible de téléverser l'image");
      return null;
    }
  };

  const handlePublicationImagesSelected = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (files.length === 0) return;

    const remaining = 10 - images.length;
    if (remaining <= 0) {
      toast.error("Maximum 10 médias");
      return;
    }

    const nextImages = [...images];
    for (const file of files.slice(0, remaining)) {
      const url = await uploadImageFile(file);
      if (!url) continue;
      nextImages.push({
        url,
        kind: "IMAGE" as const,
        texte_alternatif: file.name,
        position: nextImages.length,
      });
    }
    setValue("images_data", nextImages);
  };

  const handlePublicationVideosSelected = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (files.length === 0) return;

    const remaining = 10 - images.length;
    if (remaining <= 0) {
      toast.error("Maximum 10 médias");
      return;
    }

    const nextImages = [...images];
    for (const file of files.slice(0, remaining)) {
      if (!file.type.startsWith("video/")) {
        toast.error("Choisis une vidéo (mp4, webm, mov)");
        continue;
      }
      if (file.size > MAX_VIDEO_BYTES) {
        toast.error("Vidéo trop lourde (max 50 Mo)");
        continue;
      }
      try {
        const uploaded = await uploadForumMedia({
          file,
          kind: "VIDEO",
        }).unwrap();
        nextImages.push({
          url: uploaded.url,
          kind: "VIDEO",
          texte_alternatif: file.name,
          position: nextImages.length,
        });
      } catch {
        toast.error("Impossible de téléverser la vidéo");
      }
    }
    setValue("images_data", nextImages);
  };

  const handleOptionImageSelected = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    const index = optionImageTarget;
    event.target.value = "";
    setOptionImageTarget(null);
    if (!file || index == null) return;

    const url = await uploadImageFile(file);
    if (!url) return;

    const nextOptions = optionsData.map((option, optionIndex) =>
      optionIndex === index ? { ...option, image_url: url } : option
    );
    setValue("options_data", nextOptions);
  };

  const handleRemoveImage = (index: number) => {
    setValue(
      "images_data",
      images
        .filter((_, i) => i !== index)
        .map((image, position) => ({ ...image, position }))
    );
  };

  const handleRemoveOptionImage = (index: number) => {
    setValue(
      "options_data",
      optionsData.map((option, optionIndex) =>
        optionIndex === index ? { ...option, image_url: "" } : option
      )
    );
  };

  const handleRemoveOption = (index: number) => {
    if (optionsData.length <= 2) {
      toast.error("Il faut au moins deux options");
      return;
    }
    setValue(
      "options_data",
      optionsData
        .filter((_, optionIndex) => optionIndex !== index)
        .map((option, position) => ({ ...option, position }))
    );
  };

  const onSubmit = handleSubmit(async (values) => {
    try {
      if (mode === "APPLICATION") {
        const created = await createApplication({
          titre: values.titre,
          description: values.description,
          lien_app: values.lien_app || "",
          plateforme_app: values.plateforme_app || "WEB",
          images_data: values.images_data ?? [],
        }).unwrap();
        toast.success("Application publiée");
        resetForm();
        onCreated?.(created.id);
        return;
      }

      if (mode === "ENTRAIDE") {
        const created = await createEntraide({
          titre: values.titre,
          description: values.description,
          images_data: values.images_data ?? [],
        }).unwrap();
        toast.success("Demande d'entraide publiée");
        resetForm();
        onCreated?.(created.id);
        return;
      }

      if (mode === "CHOIX") {
        const created = await createChoix({
          titre: values.titre,
          description: values.description,
          contraintes: "",
          options_data: (values.options_data || []).map((option, position) => ({
            libelle: option.libelle,
            description: option.description,
            image_url: option.image_url || "",
            position,
          })),
          images_data: values.images_data ?? [],
        }).unwrap();
        toast.success("Aide au choix publiée");
        resetForm();
        onCreated?.(created.id);
        return;
      }

      const created = await createDiscussion({
        titre: values.titre,
        description: values.description,
        images_data: values.images_data ?? [],
        ...(espaceId ? { espace_id: espaceId } : {}),
      }).unwrap();
      toast.success("Discussion publiée");
      resetForm();
      onCreated?.(created.id);
    } catch {
      toast.error(
        mode === "APPLICATION"
          ? "Impossible de publier l'application"
          : mode === "ENTRAIDE"
            ? "Impossible de publier l'entraide"
            : mode === "CHOIX"
              ? "Impossible de publier l'aide au choix"
              : "Impossible de publier la discussion"
      );
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      {!discussionOnly ? (
      <div className="flex flex-wrap gap-2" role="group" aria-label="Type de publication">
        <Button
          type="button"
          size="sm"
          variant={mode === "DISCUSSION" ? "default" : "outline"}
          className="gap-1.5"
          aria-pressed={mode === "DISCUSSION"}
          onClick={() => onModeChange("DISCUSSION")}
        >
          <MessageSquareText className="h-3.5 w-3.5" />
          Discussion
        </Button>
        <Button
          type="button"
          size="sm"
          variant={mode === "APPLICATION" ? "default" : "outline"}
          className="gap-1.5"
          aria-pressed={mode === "APPLICATION"}
          onClick={() => onModeChange("APPLICATION")}
        >
          <AppWindow className="h-3.5 w-3.5" />
          Application
        </Button>
        <Button
          type="button"
          size="sm"
          variant={mode === "ENTRAIDE" ? "default" : "outline"}
          className="gap-1.5"
          aria-pressed={mode === "ENTRAIDE"}
          onClick={() => onModeChange("ENTRAIDE")}
        >
          <LifeBuoy className="h-3.5 w-3.5" />
          Entraide
        </Button>
        <Button
          type="button"
          size="sm"
          variant={mode === "CHOIX" ? "default" : "outline"}
          className="gap-1.5"
          aria-pressed={mode === "CHOIX"}
          onClick={() => onModeChange("CHOIX")}
        >
          <Scale className="h-3.5 w-3.5" />
          Choix
        </Button>
      </div>
      ) : null}

      <div className="space-y-1">
        <label htmlFor="forum-composer-titre" className="sr-only">
          Titre
        </label>
        <Input
          id="forum-composer-titre"
          placeholder={
            mode === "APPLICATION"
              ? "Nom de l'application"
              : mode === "ENTRAIDE"
                ? "Quel est ton problème technique ?"
                : mode === "CHOIX"
                  ? "Sur quoi hésites-tu ?"
                  : "Titre de la discussion"
          }
          className="border-0 bg-transparent px-0 text-base font-semibold shadow-none focus-visible:ring-0"
          {...register("titre")}
        />
        {errors.titre ? (
          <p className="text-xs text-destructive">{errors.titre.message}</p>
        ) : null}
      </div>

      <div className="relative space-y-1">
        <label htmlFor="forum-composer-description" className="sr-only">
          Description
        </label>
        <Textarea
          id="forum-composer-description"
          rows={4}
          placeholder={
            mode === "APPLICATION"
              ? "Décris ton app, ce qu'elle fait, pour qui…"
              : mode === "ENTRAIDE"
                ? "Explique le bug, colle le code (```python … ```), ajoute le contexte…"
                : mode === "CHOIX"
                  ? "Contexte de la décision à prendre…"
                  : "Développe ton idée, ta question ou ton retour d'expérience…"
          }
          className="min-h-24 resize-none border-0 bg-transparent px-0 font-sans shadow-none focus-visible:ring-0"
          {...descriptionRegister}
          ref={(node) => {
            descriptionRegister.ref(node);
            descriptionRef.current = node;
          }}
        />
        {errors.description ? (
          <p className="text-xs text-destructive">
            {errors.description.message}
          </p>
        ) : null}
        {mentionOpen ? (
          <div className="absolute left-0 right-0 top-full z-20 mt-1 overflow-hidden rounded-xl border border-border bg-card shadow-lg">
            <div className="border-b border-border p-2">
              <Input
                autoFocus
                value={mentionQuery}
                onChange={(event) => setMentionQuery(event.target.value)}
                placeholder="Chercher un membre…"
                className="h-8"
              />
            </div>
            <ul className="max-h-48 overflow-y-auto p-1">
              {mentionQuery.trim().length < 1 ? (
                <li className="px-3 py-2 text-xs text-muted-foreground">
                  Tape un nom ou un pseudo…
                </li>
              ) : null}
              {mentionQuery.trim().length >= 1 && searchingMembres ? (
                <li className="px-3 py-2 text-xs text-muted-foreground">
                  Recherche…
                </li>
              ) : null}
              {mentionQuery.trim().length >= 1 &&
              !searchingMembres &&
              mentionResults.length === 0 ? (
                <li className="px-3 py-2 text-xs text-muted-foreground">
                  Aucun membre trouvé.
                </li>
              ) : null}
              {mentionResults.map((membre) => (
                <li key={membre.id}>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-muted"
                    onClick={() => insertMention(membre.username)}
                  >
                    <ForumAvatar
                      name={membre.full_name || membre.username}
                      photo={membre.photo}
                      size="sm"
                      tone="soft"
                    />
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium text-foreground">
                        {membre.full_name || membre.username}
                      </span>
                      <span className="block truncate text-xs text-muted-foreground">
                        @{membre.username}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      {mode === "APPLICATION" ? (
        <div className="space-y-2">
          <label htmlFor="forum-composer-lien" className="sr-only">
            Lien de l&apos;application
          </label>
          <Input
            id="forum-composer-lien"
            placeholder="Lien HTTP(S) pour essayer l'app"
            {...register("lien_app")}
          />
          {errors.lien_app?.message ? (
            <p className="text-xs text-destructive">{errors.lien_app.message}</p>
          ) : null}
          <label htmlFor="forum-composer-plateforme" className="sr-only">
            Plateforme
          </label>
          <select
            id="forum-composer-plateforme"
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
            {...register("plateforme_app")}
          >
            <option value="WEB">Web</option>
            <option value="MOBILE">Mobile</option>
            <option value="LES_DEUX">Web et mobile</option>
          </select>
        </div>
      ) : null}

      {mode === "CHOIX" ? (
        <div className="space-y-3">
          {optionsData.map((option, index) => (
            <div
              key={`option-${index}`}
              className="space-y-2 rounded-lg border border-border p-3"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-medium text-muted-foreground">
                  Option {index + 1}
                </p>
                <button
                  type="button"
                  aria-label={`Supprimer l'option ${index + 1}`}
                  disabled={optionsData.length <= 2}
                  title={
                    optionsData.length <= 2
                      ? "Au moins deux options sont requises"
                      : "Supprimer cette option"
                  }
                  className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-destructive disabled:cursor-not-allowed disabled:opacity-40"
                  onClick={() => handleRemoveOption(index)}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <Input
                placeholder="Libellé"
                {...register(`options_data.${index}.libelle` as const)}
              />
              <Textarea
                rows={2}
                placeholder="Précision (optionnel)"
                {...register(`options_data.${index}.description` as const)}
              />
              {option.image_url ? (
                <div className="relative w-full max-w-[10rem] overflow-hidden rounded-lg border border-border">
                  <img
                    src={buildMediaUrl(option.image_url)}
                    alt={`Option ${index + 1}`}
                    className="h-24 w-full object-cover"
                  />
                  <button
                    type="button"
                    aria-label="Retirer l'image de l'option"
                    className="absolute right-1 top-1 rounded-md bg-background/90 p-1 text-muted-foreground hover:text-foreground"
                    onClick={() => handleRemoveOptionImage(index)}
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="gap-1.5"
                  disabled={uploadingImage}
                  onClick={() => {
                    setOptionImageTarget(index);
                    optionImageInputRef.current?.click();
                  }}
                >
                  <ImageIcon className="h-3.5 w-3.5" />
                  Image de l&apos;option
                </Button>
              )}
            </div>
          ))}
          {errors.options_data?.message ? (
            <p className="text-xs text-destructive">
              {errors.options_data.message as string}
            </p>
          ) : null}
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() =>
              setValue("options_data", [
                ...optionsData,
                {
                  libelle: "",
                  description: "",
                  image_url: "",
                  position: optionsData.length,
                },
              ])
            }
          >
            Ajouter une option
          </Button>
        </div>
      ) : null}

      {images.length > 0 ? (
        <ul className="flex flex-wrap gap-2">
          {images.map((image, index) => (
            <li
              key={`${image.url}-${index}`}
              className="relative h-20 w-20 overflow-hidden rounded-lg border border-border bg-muted"
            >
              {image.kind === "VIDEO" ? (
                <video
                  src={buildMediaUrl(image.url)}
                  className="h-full w-full object-cover"
                  muted
                  preload="metadata"
                />
              ) : (
                <img
                  src={buildMediaUrl(image.url)}
                  alt={image.texte_alternatif || `Média ${index + 1}`}
                  className="h-full w-full object-cover"
                />
              )}
              <button
                type="button"
                aria-label="Retirer le média"
                className="absolute right-1 top-1 rounded-md bg-background/90 p-1 text-muted-foreground hover:text-foreground"
                onClick={() => handleRemoveImage(index)}
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      <input
        ref={publicationImageInputRef}
        type="file"
        accept={IMAGE_ACCEPT}
        multiple
        className="hidden"
        onChange={handlePublicationImagesSelected}
      />
      <input
        ref={publicationVideoInputRef}
        type="file"
        accept={VIDEO_ACCEPT}
        multiple
        className="hidden"
        onChange={handlePublicationVideosSelected}
      />
      <input
        ref={optionImageInputRef}
        type="file"
        accept={IMAGE_ACCEPT}
        className="hidden"
        onChange={handleOptionImageSelected}
      />

      <div className="flex flex-col gap-3 border-t border-border pt-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-1.5"
            disabled={
              uploadingImage || uploadingVideo || images.length >= 10
            }
            onClick={() => publicationImageInputRef.current?.click()}
          >
            {uploadingImage ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <ImageIcon className="h-3.5 w-3.5" />
            )}
            Images
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-1.5"
            disabled={
              uploadingImage || uploadingVideo || images.length >= 10
            }
            onClick={() => publicationVideoInputRef.current?.click()}
          >
            {uploadingVideo ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Video className="h-3.5 w-3.5" />
            )}
            Vidéo
          </Button>
          <Button
            type="button"
            variant={mentionOpen ? "secondary" : "outline"}
            size="sm"
            className="gap-1.5"
            aria-pressed={mentionOpen}
            onClick={() => setMentionOpen((open) => !open)}
          >
            <AtSign className="h-3.5 w-3.5" />
            Mentionner
          </Button>
          <span className="text-xs text-muted-foreground">
            {images.length}/10 · images 5 Mo · vidéos 50 Mo
          </span>
        </div>

        <div className="flex items-center justify-end gap-2">
          <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
            Annuler
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={isLoading}
            className={cn(
              "gap-1.5 bg-brand text-brand-foreground hover:bg-brand/90"
            )}
          >
            <SendHorizontal className="h-3.5 w-3.5" />
            {isLoading ? "Publication…" : "Publier"}
          </Button>
        </div>
      </div>
    </form>
  );
}

export function FeedComposer({
  onCreated,
  espaceId = null,
  discussionOnly = false,
}: FeedComposerProps) {
  const user = useAuthSlice((state) => state.user);
  const [expanded, setExpanded] = useState(false);
  const [mode, setMode] = useState<ComposerMode>("DISCUSSION");
  const displayName = user?.full_name || user?.username || "Vous";

  return (
    <section className="rounded-2xl border border-border bg-card p-4 shadow-sm sm:p-5">
      <div className="flex gap-3">
        <ForumAvatar
          name={displayName}
          photo={user?.photo}
          tone="brand"
        />

        <div className="min-w-0 flex-1">
          {!expanded ? (
            <button
              type="button"
              onClick={() => setExpanded(true)}
              className="flex w-full items-center rounded-xl border border-border bg-muted/50 px-4 py-3 text-left text-sm text-muted-foreground transition-colors hover:bg-muted"
            >
              {espaceId
                ? "Écrire une discussion dans cette communauté…"
                : "Partager un projet, une astuce de code ou poser une question…"}
            </button>
          ) : (
            <ComposerForm
              key={mode}
              mode={mode}
              onModeChange={setMode}
              espaceId={espaceId}
              discussionOnly={discussionOnly || Boolean(espaceId)}
              onCreated={(id) => {
                setExpanded(false);
                setMode("DISCUSSION");
                onCreated?.(id);
              }}
              onCancel={() => {
                setExpanded(false);
                setMode("DISCUSSION");
              }}
            />
          )}
        </div>
      </div>
    </section>
  );
}
