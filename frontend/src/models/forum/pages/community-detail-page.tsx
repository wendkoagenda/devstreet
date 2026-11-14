import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  Camera,
  Copy,
  Loader2,
  Link2,
  Settings,
  UserMinus,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import {
  useCreateEspaceLienMutation,
  useExclureEspaceMembreMutation,
  useGetEspaceLiensQuery,
  useGetEspaceMembresQuery,
  useGetEspaceQuery,
  useGetPublicationsInfiniteQuery,
  useQuitterEspaceMutation,
  useRejoindreEspaceMutation,
  useRejoindreViaInvitationMutation,
  useRevoquerEspaceLienMutation,
  useSetEspaceMembreRoleMutation,
  useUpdateEspaceMutation,
  useUploadForumImageMutation,
} from "../api";
import { EspaceChat } from "../components/espace-chat";
import { FeedComposer } from "../components/feed-composer";
import { ForumAvatar } from "../components/forum-avatar";
import { PublicationCard } from "../components/publication-card";

export default function CommunityDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const inviteCode = searchParams.get("invite") || undefined;
  const espaceId = Number(id);
  const skip = !Number.isFinite(espaceId) || espaceId <= 0;
  const [settingsOpen, setSettingsOpen] = useState(false);

  const {
    data: espace,
    isLoading,
    isError,
    refetch,
  } = useGetEspaceQuery(
    inviteCode ? { id: espaceId, invite: inviteCode } : espaceId,
    { skip }
  );

  const {
    data: feed,
    isLoading: feedLoading,
    isFetching,
    isError: feedError,
    fetchNextPage,
    hasNextPage,
    refetch: refetchFeed,
  } = useGetPublicationsInfiniteQuery(
    {
      espace: espaceId,
      page_size: PAGE_SIZE,
      ...(inviteCode ? { invite: inviteCode } : {}),
    },
    {
      skip:
        skip ||
        espace?.type !== "CHAINE" ||
        (espace?.can_read === false && !espace?.mon_role),
    }
  );

  const isAdmin =
    espace?.mon_role === "SUPER_ADMIN" || espace?.mon_role === "ADMIN";
  const isSuperAdmin = espace?.mon_role === "SUPER_ADMIN";

  const { data: liens } = useGetEspaceLiensQuery(espaceId, {
    skip: skip || !isAdmin || !settingsOpen || espace?.acces !== "LIEN",
  });
  const { data: membresData, refetch: refetchMembres } =
    useGetEspaceMembresQuery(espaceId, {
      skip: skip || !settingsOpen || !isAdmin,
    });

  const [rejoindre, { isLoading: joining }] = useRejoindreEspaceMutation();
  const [quitter, { isLoading: leaving }] = useQuitterEspaceMutation();
  const [rejoindreInvite, { isLoading: joiningInvite }] =
    useRejoindreViaInvitationMutation();
  const [updateEspace, { isLoading: updating }] = useUpdateEspaceMutation();
  const [createLien, { isLoading: creatingLien }] =
    useCreateEspaceLienMutation();
  const [revoquerLien] = useRevoquerEspaceLienMutation();
  const [setRole] = useSetEspaceMembreRoleMutation();
  const [exclureMembre] = useExclureEspaceMembreMutation();
  const [uploadForumImage, { isLoading: uploadingPhoto }] =
    useUploadForumImageMutation();
  const photoInputRef = useRef<HTMLInputElement | null>(null);
  const [freshCode, setFreshCode] = useState<string | null>(null);
  const [withPreview, setWithPreview] = useState(true);
  const [editNom, setEditNom] = useState("");
  const [editDescription, setEditDescription] = useState("");

  const publications =
    feed?.pages.flatMap((page) => page.results ?? []) ?? [];
  const isChannel = espace?.type === "CHAINE";
  const listPath = isChannel ? "/forum/chaines" : "/forum/communautes";
  const spaceLabel = isChannel ? "chaîne" : "communauté";
  const isMember = Boolean(espace?.mon_role);
  const canPublish = Boolean(espace?.can_publish);
  const canRead = espace?.can_read !== false || isMember;
  const canLeave = isMember && !isSuperAdmin;
  const manageMode = searchParams.get("manage") === "1";

  // Membre : chat / annonces vivent dans Messages (sauf panneau Infos).
  useEffect(() => {
    if (!espace || skip) return;
    if (!espace.mon_role) return;
    if (manageMode) {
      setSettingsOpen(true);
      return;
    }
    navigate(`/messages?groupe=${espace.id}`, { replace: true });
  }, [espace, skip, manageMode, navigate]);

  const inviteUrl = useMemo(() => {
    if (!freshCode) return null;
    return `${window.location.origin}/forum/invitation/${freshCode}`;
  }, [freshCode]);

  const handleJoin = async () => {
    try {
      if (inviteCode) {
        await rejoindreInvite(inviteCode).unwrap();
      } else {
        await rejoindre(espaceId).unwrap();
      }
      toast.success(
        isChannel ? "Tu es abonné à la chaîne" : "Tu as rejoint la communauté"
      );
      navigate(`/messages?groupe=${espaceId}`, { replace: true });
    } catch {
      toast.error(
        isChannel
          ? "Impossible de s'abonner à cette chaîne"
          : "Impossible de rejoindre cette communauté"
      );
    }
  };

  const handleLeave = async () => {
    try {
      await quitter(espaceId).unwrap();
      toast.success(
        isChannel ? "Tu t'es désabonné" : "Tu as quitté la communauté"
      );
      void refetch();
    } catch {
      toast.error(
        isChannel
          ? "Impossible de se désabonner"
          : "Impossible de quitter la communauté"
      );
    }
  };

  const handleTogglePublish = async () => {
    if (!espace) return;
    try {
      await updateEspace({
        id: espace.id,
        membres_peuvent_publier: !espace.membres_peuvent_publier,
      }).unwrap();
      toast.success("Règle d'écriture mise à jour");
      void refetch();
    } catch {
      toast.error("Impossible de modifier la règle");
    }
  };

  const handleToggleAcces = async () => {
    if (!espace) return;
    try {
      await updateEspace({
        id: espace.id,
        acces: espace.acces === "PUBLIC" ? "LIEN" : "PUBLIC",
      }).unwrap();
      toast.success("Mode d'accès mis à jour");
      void refetch();
    } catch {
      toast.error("Impossible de changer l'accès");
    }
  };

  const handleToggleCommentaires = async () => {
    if (!espace) return;
    try {
      await updateEspace({
        id: espace.id,
        commentaires_ouverts: !espace.commentaires_ouverts,
      }).unwrap();
      toast.success(
        espace.commentaires_ouverts
          ? "Commentaires fermés"
          : "Commentaires rouverts"
      );
      void refetch();
    } catch {
      toast.error("Impossible de modifier les commentaires");
    }
  };

  const handleCreateLien = async () => {
    try {
      const created = await createLien({
        espaceId,
        previsualisation_autorisee: withPreview,
      }).unwrap();
      setFreshCode(created.code || null);
      toast.success("Lien créé — copie-le maintenant");
    } catch {
      toast.error("Impossible de créer le lien");
    }
  };

  const handleCopy = async () => {
    if (!inviteUrl) return;
    try {
      await navigator.clipboard.writeText(inviteUrl);
      toast.success("Lien copié");
    } catch {
      toast.error("Copie impossible");
    }
  };

  const openSettings = () => {
    if (!espace) return;
    setEditNom(espace.nom);
    setEditDescription(espace.description || "");
    setSettingsOpen(true);
  };

  const handleSaveInfos = async () => {
    if (!espace) return;
    try {
      await updateEspace({
        id: espace.id,
        nom: editNom.trim(),
        description: editDescription.trim(),
      }).unwrap();
      toast.success("Infos mises à jour");
      void refetch();
    } catch {
      toast.error("Impossible d'enregistrer");
    }
  };

  const handlePhotoSelected = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !espace) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Choisis une image");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image trop lourde (max 5 Mo)");
      return;
    }
    try {
      const uploaded = await uploadForumImage(file).unwrap();
      await updateEspace({ id: espace.id, photo: uploaded.url }).unwrap();
      toast.success("Photo mise à jour");
      void refetch();
    } catch {
      toast.error("Impossible de changer la photo");
    }
  };

  if (skip) {
    return (
      <div className="mx-auto max-w-3xl py-10 text-center">
        <p className="text-sm text-destructive">Espace introuvable.</p>
        <Button asChild className="mt-4" variant="outline">
          <Link to="/forum/communautes">Retour</Link>
        </Button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <p className="mx-auto max-w-3xl py-10 text-center text-sm text-muted-foreground">
        Chargement…
      </p>
    );
  }

  if (isError || !espace) {
    return (
      <div className="mx-auto max-w-3xl space-y-3 py-10 text-center">
        <p className="text-sm text-destructive">
          Impossible de charger cet espace.
        </p>
        <Button type="button" variant="outline" onClick={() => refetch()}>
          Réessayer
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4">
      <div className="flex items-center justify-between gap-2">
        <Button asChild variant="ghost" className="-ml-2 gap-2">
          <Link to={listPath}>
            <ArrowLeft className="h-4 w-4" />
            {isChannel ? "Chaînes" : "Communautés"}
          </Link>
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label={
            isAdmin ? `Réglages de la ${spaceLabel}` : `Infos de la ${spaceLabel}`
          }
          title={isAdmin ? "Réglages" : "Infos"}
          onClick={openSettings}
        >
          <Settings className="h-5 w-5" />
        </Button>
      </div>

      <header className="rounded-2xl border border-border bg-card p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex min-w-0 items-start gap-3">
            <ForumAvatar
              name={espace.nom}
              photo={espace.photo}
              size="xl"
              tone="soft"
            />
            <div className="min-w-0">
              <h1 className="text-xl font-semibold tracking-tight text-foreground">
                {espace.nom}
              </h1>
              {espace.description ? (
                <p className="mt-1 text-sm text-muted-foreground">
                  {espace.description}
                </p>
              ) : null}
              <p className="mt-2 inline-flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                <Users className="h-3.5 w-3.5" aria-hidden />
                {espace.membres_count ?? 0}{" "}
                {isChannel
                  ? `abonné${(espace.membres_count ?? 0) > 1 ? "s" : ""}`
                  : `membre${(espace.membres_count ?? 0) > 1 ? "s" : ""}`}
                <span>
                  · {espace.acces === "LIEN" ? "par lien" : "public"}
                </span>
                <span>
                  ·{" "}
                  {isChannel
                    ? "fil d'annonces"
                    : "chat de groupe"}
                </span>
                {espace.mon_role ? (
                  <span className="text-brand">
                    ·{" "}
                    {espace.mon_role === "SUPER_ADMIN"
                      ? "super admin"
                      : espace.mon_role === "ADMIN"
                        ? "admin"
                        : isChannel
                          ? "abonné"
                          : "membre"}
                  </span>
                ) : null}
                {espace.via_preview ? <span>· prévisualisation</span> : null}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {!isMember ? (
              <Button
                type="button"
                disabled={joining || joiningInvite}
                onClick={handleJoin}
              >
                {joining || joiningInvite ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : null}
                {isChannel ? "S'abonner" : "Rejoindre"}
              </Button>
            ) : null}
            {canLeave ? (
              <Button
                type="button"
                variant="outline"
                disabled={leaving}
                onClick={handleLeave}
              >
                {leaving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                {isChannel ? "Se désabonner" : "Quitter"}
              </Button>
            ) : null}
          </div>
        </div>
      </header>

      {!isChannel ? (
        isMember || espace.via_preview ? (
          <EspaceChat
            espaceId={espace.id}
            canWrite={canPublish}
            canReact={isMember}
            canModerate={isAdmin}
            readOnlyHint={
              isMember && !canPublish
                ? "Seuls les administrateurs peuvent écrire ici."
                : undefined
            }
          />
        ) : (
          <p className="rounded-xl border border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
            Rejoins la communauté pour discuter avec les membres.
          </p>
        )
      ) : (
        <>
          {canPublish ? (
            <FeedComposer
              espaceId={espace.id}
              discussionOnly
              onCreated={() => {
                void refetchFeed();
              }}
            />
          ) : isMember ? (
            <p className="rounded-xl border border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
              Seuls les administrateurs publient des nouveautés ici.
            </p>
          ) : (
            <p className="rounded-xl border border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
              Abonne-toi pour voir les nouveautés de la chaîne.
            </p>
          )}

          {canRead && feedLoading ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              Chargement du fil…
            </p>
          ) : null}

          {canRead && feedError ? (
            <div className="space-y-3 py-6 text-center">
              <p className="text-sm text-destructive">
                Impossible de charger les publications.
              </p>
              <Button
                type="button"
                variant="outline"
                onClick={() => refetchFeed()}
              >
                Réessayer
              </Button>
            </div>
          ) : null}

          {canRead ? (
            <div className="space-y-3">
              {publications.map((publication) => (
                <PublicationCard
                  key={publication.id}
                  publication={publication}
                />
              ))}
              {!feedLoading && !feedError && publications.length === 0 ? (
                <p className="rounded-2xl border border-dashed border-border px-4 py-10 text-center text-sm text-muted-foreground">
                  Aucune nouveauté pour l’instant.
                </p>
              ) : null}
            </div>
          ) : null}

          {canRead && hasNextPage ? (
            <div className="flex justify-center">
              <Button
                type="button"
                variant="outline"
                disabled={isFetching}
                onClick={() => fetchNextPage()}
              >
                {isFetching ? "Chargement…" : "Voir plus"}
              </Button>
            </div>
          ) : null}
        </>
      )}

      <Sheet open={settingsOpen} onOpenChange={setSettingsOpen}>
        <SheetContent
          side="right"
          className="w-full overflow-y-auto sm:max-w-md"
        >
          <SheetHeader>
            <SheetTitle>
              {isAdmin ? "Réglages du groupe" : "Infos du groupe"}
            </SheetTitle>
            <SheetDescription>
              {isAdmin
                ? `Photo, détails, droits et ${isChannel ? "abonnés" : "membres"}.`
                : isChannel
                  ? "Les annonces s’affichent dans Messages."
                  : "La discussion s’affiche dans Messages."}
            </SheetDescription>
          </SheetHeader>

          <div className="mt-6 space-y-6">
            <section className="flex flex-col items-center gap-3 border-b border-border pb-6">
              <div className="relative">
                <ForumAvatar
                  name={espace.nom}
                  photo={espace.photo}
                  size="xl"
                  tone="soft"
                  className="h-24 w-24 text-xl"
                />
                {isAdmin ? (
                  <>
                    <Button
                      type="button"
                      size="icon"
                      className="absolute bottom-0 right-0 h-8 w-8 rounded-full"
                      disabled={uploadingPhoto || updating}
                      aria-label="Changer la photo"
                      onClick={() => photoInputRef.current?.click()}
                    >
                      {uploadingPhoto ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Camera className="h-3.5 w-3.5" />
                      )}
                    </Button>
                    <input
                      ref={photoInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/gif,image/webp"
                      className="hidden"
                      onChange={handlePhotoSelected}
                    />
                  </>
                ) : null}
              </div>
              {isAdmin ? (
                <p className="text-center text-sm text-muted-foreground">
                  Appuie sur l&apos;appareil photo pour changer l&apos;image
                </p>
              ) : (
                <div className="space-y-1 text-center">
                  <p className="text-sm font-medium text-foreground">
                    {espace.nom}
                  </p>
                  {espace.description ? (
                    <p className="text-sm text-muted-foreground">
                      {espace.description}
                    </p>
                  ) : null}
                </div>
              )}
            </section>

            {isAdmin ? (
              <section className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">
                  Nom et description
                </h3>
                <Input
                  value={editNom}
                  onChange={(event) => setEditNom(event.target.value)}
                  maxLength={120}
                  placeholder="Nom"
                />
                <Textarea
                  value={editDescription}
                  onChange={(event) => setEditDescription(event.target.value)}
                  placeholder="Description"
                  className="min-h-[72px]"
                />
                <Button
                  type="button"
                  size="sm"
                  disabled={updating}
                  onClick={handleSaveInfos}
                >
                  Enregistrer
                </Button>
              </section>
            ) : null}

            {isSuperAdmin ? (
              <section className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">
                  Droits du groupe
                </h3>
                <div className="flex flex-col gap-2">
                  {!isChannel ? (
                    <Button
                      type="button"
                      variant="outline"
                      className="justify-start"
                      disabled={updating}
                      onClick={handleTogglePublish}
                    >
                      Messages :{" "}
                      {espace.membres_peuvent_publier
                        ? "tous les membres"
                        : "admins seulement"}
                    </Button>
                  ) : null}
                  <Button
                    type="button"
                    variant="outline"
                    className="justify-start"
                    disabled={updating}
                    onClick={handleToggleAcces}
                  >
                    Accès :{" "}
                    {espace.acces === "PUBLIC" ? "public" : "par lien"}
                  </Button>
                  {isChannel ? (
                    <Button
                      type="button"
                      variant="outline"
                      className="justify-start"
                      disabled={updating}
                      onClick={handleToggleCommentaires}
                    >
                      Commentaires :{" "}
                      {espace.commentaires_ouverts ? "ouverts" : "fermés"}
                    </Button>
                  ) : null}
                </div>
              </section>
            ) : null}

            {isAdmin && espace.acces === "LIEN" ? (
              <section className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">
                  Liens d&apos;invitation
                </h3>
                <label className="flex items-center gap-2 text-sm text-muted-foreground">
                  <input
                    type="checkbox"
                    checked={withPreview}
                    onChange={(event) => setWithPreview(event.target.checked)}
                  />
                  Prévisualisation avant adhésion
                </label>
                <Button
                  type="button"
                  size="sm"
                  className="gap-1.5"
                  disabled={creatingLien}
                  onClick={handleCreateLien}
                >
                  <Link2 className="h-3.5 w-3.5" />
                  Créer un lien
                </Button>
                {inviteUrl ? (
                  <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/40 px-3 py-2 text-sm">
                    <code className="min-w-0 flex-1 truncate">{inviteUrl}</code>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={handleCopy}
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ) : null}
                <ul className="space-y-2 text-sm">
                  {(liens ?? []).map((lien) => (
                    <li
                      key={lien.id}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2"
                    >
                      <span className="text-muted-foreground">
                        #{lien.id} ·{" "}
                        {lien.previsualisation_autorisee
                          ? "avec préview"
                          : "sans préview"}{" "}
                        ·{" "}
                        {lien.est_actif === false || lien.revoked_at
                          ? "révoqué"
                          : "actif"}
                      </span>
                      {lien.est_actif !== false && !lien.revoked_at ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={async () => {
                            try {
                              await revoquerLien({
                                espaceId,
                                lienId: lien.id,
                              }).unwrap();
                              toast.success("Lien révoqué");
                            } catch {
                              toast.error("Révocation impossible");
                            }
                          }}
                        >
                          Révoquer
                        </Button>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}

            {isAdmin ? (
              <section className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">
                  {isChannel ? "Abonnés" : "Membres"} (
                  {membresData?.results?.length ?? 0})
                </h3>
                <ul className="divide-y divide-border rounded-xl border border-border">
                  {(membresData?.results ?? []).map((m) => {
                    const name =
                      m.membre_detail?.full_name ||
                      m.membre_detail?.username ||
                      `Membre #${m.membre}`;
                    const canExclude =
                      m.role !== "SUPER_ADMIN" &&
                      (isSuperAdmin || m.role === "MEMBRE");
                    return (
                      <li
                        key={m.id}
                        className="flex items-center gap-3 px-3 py-2.5"
                      >
                        <ForumAvatar
                          name={name}
                          photo={m.membre_detail?.photo}
                          size="sm"
                          tone="muted"
                        />
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-foreground">
                            {name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {m.role === "SUPER_ADMIN"
                              ? "Créateur"
                              : m.role === "ADMIN"
                                ? "Admin"
                                : isChannel
                                  ? "Abonné"
                                  : "Membre"}
                          </p>
                        </div>
                        <div className="flex shrink-0 gap-1">
                          {isSuperAdmin && m.role !== "SUPER_ADMIN" ? (
                            <Button
                              type="button"
                              size="sm"
                              variant="ghost"
                              onClick={async () => {
                                try {
                                  await setRole({
                                    espaceId,
                                    membreId: m.membre,
                                    role:
                                      m.role === "ADMIN" ? "MEMBRE" : "ADMIN",
                                  }).unwrap();
                                  toast.success("Rôle mis à jour");
                                  void refetchMembres();
                                } catch {
                                  toast.error("Impossible de changer le rôle");
                                }
                              }}
                            >
                              {m.role === "ADMIN" ? "Rétrograder" : "Admin"}
                            </Button>
                          ) : null}
                          {canExclude ? (
                            <Button
                              type="button"
                              size="icon"
                              variant="ghost"
                              className="text-destructive hover:text-destructive"
                              aria-label={`Retirer ${name}`}
                              title="Retirer du groupe"
                              onClick={async () => {
                                try {
                                  await exclureMembre({
                                    espaceId,
                                    membreId: m.membre,
                                  }).unwrap();
                                  toast.success(`${name} a été retiré`);
                                  void refetch();
                                  void refetchMembres();
                                } catch {
                                  toast.error("Impossible de retirer ce membre");
                                }
                              }}
                            >
                              <UserMinus className="h-4 w-4" />
                            </Button>
                          ) : null}
                        </div>
                      </li>
                    );
                  })}
                  {(membresData?.results ?? []).length === 0 ? (
                    <li className="px-3 py-4 text-sm text-muted-foreground">
                      Aucun membre chargé.
                    </li>
                  ) : null}
                </ul>
              </section>
            ) : null}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
