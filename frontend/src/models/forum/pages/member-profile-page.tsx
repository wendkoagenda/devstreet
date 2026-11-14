import { useEffect, useMemo, useRef } from "react";
import { Link, Navigate, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  Building2,
  Code2,
  FolderKanban,
  ImageIcon,
  Mail,
  MessageSquareText,
  Pencil,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import { profilePath, type ProfileSection } from "@/helpers/routes/profile-path";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { OpenToWorkRing } from "@/components/ui/open-to-work-ring";
import { EditProfileDialog } from "@/models/auth/components/edit-profile-dialog";
import { ProfileImageEditButton } from "@/models/auth/components/profile-image-edit-button";
import { useAuthSlice } from "@/models/auth/slice";
import {
  useGetContributionsQuery,
  useGetProjectsQuery,
} from "@/models/devstreet-hub/api";
import {
  useGetPublicationsInfiniteQuery,
  useGetPublicProfileByUsernameQuery,
  useOpenConversationMutation,
  useToggleSuivreMembreMutation,
} from "../api";
import { FeedComposer } from "../components/feed-composer";
import { ForumAvatar } from "../components/forum-avatar";
import { ProfileCompanySection } from "../components/profile-company-section";
import { ProfileDevSection } from "../components/profile-dev-section";
import { PublicationCard } from "../components/publication-card";

const SECTIONS: ProfileSection[] = [
  "publications",
  "projets",
  "contributions",
  "dev",
  "entreprise",
];

function parseSection(raw: string | null): ProfileSection {
  return SECTIONS.find((item) => item === raw) ?? "publications";
}

const NAV_ITEMS: {
  id: ProfileSection;
  label: string;
  icon: typeof MessageSquareText;
}[] = [
  { id: "publications", label: "Publications", icon: MessageSquareText },
  { id: "projets", label: "Mes projets", icon: FolderKanban },
  { id: "contributions", label: "Contributions", icon: Sparkles },
  { id: "dev", label: "Profil dev", icon: Code2 },
  { id: "entreprise", label: "Entreprise", icon: Building2 },
];

const ME_ALIASES = ["me", "moi"];

export default function MemberProfilePage() {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const currentUser = useAuthSlice((state) => state.user);
  const currentUserId = currentUser?.id ?? null;

  const rawUsername = (params.username ?? "").trim();
  const isMeAlias = ME_ALIASES.includes(rawUsername.toLowerCase());
  const section = parseSection(searchParams.get("section"));
  const [editOpen, setEditOpen] = useState(false);

  const setSection = (next: ProfileSection) => {
    const nextParams = new URLSearchParams(searchParams);
    if (next === "publications") nextParams.delete("section");
    else nextParams.set("section", next);
    setSearchParams(nextParams, { replace: true });
  };

  const {
    data: profile,
    isLoading: profileLoading,
    isError: profileError,
    refetch: refetchProfile,
  } = useGetPublicProfileByUsernameQuery(rawUsername, {
    skip: !rawUsername || isMeAlias,
  });

  // ?edit=1 : ouvre « Modifier le profil » sur mon propre profil (le paramètre est ensuite retiré de l'adresse)
  useEffect(() => {
    if (searchParams.get("edit") !== "1" || !profile || !currentUserId) return;
    if (Number(currentUserId) === profile.id) setEditOpen(true);
    const next = new URLSearchParams(searchParams);
    next.delete("edit");
    setSearchParams(next, { replace: true });
  }, [searchParams, profile, currentUserId, setSearchParams]);

  // Adresse canonique : /profil/<nom> avec la casse exacte du nom d'utilisateur
  useEffect(() => {
    if (profile?.username && profile.username !== rawUsername) {
      navigate(
        {
          pathname: `/profil/${encodeURIComponent(profile.username)}`,
          search: searchParams.toString() ? `?${searchParams.toString()}` : "",
        },
        { replace: true }
      );
    }
  }, [profile?.username, rawUsername, navigate, searchParams]);

  if (isMeAlias) {
    if (currentUser?.username) {
      return (
        <Navigate
          to={{
            pathname: `/profil/${encodeURIComponent(currentUser.username)}`,
            search: searchParams.toString() ? `?${searchParams.toString()}` : "",
          }}
          replace
        />
      );
    }
    return <Navigate to="/welcome" replace />;
  }

  if (!rawUsername) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center text-sm text-muted-foreground">
        Profil introuvable.
      </div>
    );
  }

  if (profileLoading && !profile) {
    return (
      <div className="mx-auto max-w-5xl py-16 text-center text-sm text-muted-foreground">
        Chargement du profil…
      </div>
    );
  }

  if (profileError || !profile) {
    return (
      <div className="mx-auto max-w-lg py-16 text-center text-sm text-muted-foreground">
        Profil introuvable.
      </div>
    );
  }

  const userId = profile.id;
  const isOwnProfile =
    currentUserId != null && Number(currentUserId) === userId;
  const displayName = profile.full_name || profile.username || "Membre";
  const handle = profile.username ? `@${profile.username}` : "";
  const photo = profile.photo || (isOwnProfile ? currentUser?.photo : "") || "";
  const banner =
    profile.banner || (isOwnProfile ? currentUser?.banner : "") || "";
  const bannerUrl = banner ? buildMediaUrl(banner) : null;

  return (
    <div className="mx-auto w-full max-w-5xl space-y-5">
      <section className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
        <div className="relative h-40 bg-muted sm:h-52">
          {bannerUrl ? (
            <img
              src={bannerUrl}
              alt=""
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-muted-foreground">
              <ImageIcon className="h-10 w-10" aria-hidden />
            </div>
          )}
          {isOwnProfile ? (
            <ProfileImageEditButton
              kind="banner"
              hasImage={Boolean(bannerUrl)}
              onUpdated={() => void refetchProfile()}
              className="absolute right-3 top-3"
            />
          ) : null}
        </div>

        <div className="relative px-4 pb-4 sm:px-6">
          <div className="-mt-12 flex flex-col gap-4 sm:-mt-14 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex items-end gap-4">
              <div className="relative rounded-full border-4 border-card bg-card">
                <ForumAvatar
                  name={displayName}
                  photo={photo}
                  tone="soft"
                  className="!h-24 !w-24 !text-lg sm:!h-28 sm:!w-28"
                />
                {isOwnProfile ? (
                  <ProfileImageEditButton
                    kind="photo"
                    hasImage={Boolean(photo)}
                    onUpdated={() => void refetchProfile()}
                    // Sur le côté : le bas de la photo porte l'arc « Open to work »
                    className="absolute -right-4 top-1/2 -translate-y-1/2 flex-col"
                  />
                ) : null}
                {profile.profil_dev?.is_open_to_work ? <OpenToWorkRing /> : null}
              </div>
              <div className="min-w-0 pb-1">
                <h1 className="truncate text-xl font-bold tracking-tight text-foreground sm:text-2xl">
                  {displayName}
                </h1>
                {handle ? (
                  <p className="truncate text-sm text-muted-foreground">
                    {handle}
                  </p>
                ) : null}
                <p className="mt-0.5 text-xs text-muted-foreground">
                  <span className="font-semibold text-foreground">
                    {profile.connections_count}
                  </span>{" "}
                  {profile.connections_count > 1 ? "connexions" : "connexion"}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 self-start sm:self-auto">
              {isOwnProfile ? (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setEditOpen(true)}
                >
                  <Pencil className="mr-2 h-4 w-4" />
                  Modifier le profil
                </Button>
              ) : (
                <>
                  <FollowProfileButton
                    userId={userId}
                    isFollowing={Boolean(profile?.is_following)}
                  />
                  <MessageProfileButton userId={userId} />
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside className="space-y-2 lg:sticky lg:top-4 lg:self-start">
          <nav className="rounded-2xl border border-border bg-card p-2 shadow-sm">
            {NAV_ITEMS.filter((item) => {
              // Les onglets Profil dev et Entreprise n'apparaissent que si le profil existe
              // (ou, sur son propre profil, pour proposer de le créer)
              if (item.id === "dev") return Boolean(profile.profil_dev) || isOwnProfile;
              if (item.id === "entreprise")
                return Boolean(profile.profil_entreprise) || isOwnProfile;
              return true;
            }).map((item) => {
              const Icon = item.icon;
              const active = section === item.id;
              const label =
                item.id === "projets" && !isOwnProfile
                  ? "Projets"
                  : item.id === "contributions" && !isOwnProfile
                    ? "Contributions"
                    : item.label;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSection(item.id)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition-colors",
                    active
                      ? "bg-brand-soft text-brand-strong"
                      : "text-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" aria-hidden />
                  {label}
                </button>
              );
            })}
          </nav>
        </aside>

        <div className="min-w-0 space-y-4">
          {section === "publications" ? (
            <ProfilePublications
              userId={userId}
              isOwnProfile={isOwnProfile}
            />
          ) : null}
          {section === "projets" ? <ProfileProjects userId={userId} /> : null}
          {section === "contributions" ? (
            <ProfileContributions userId={userId} />
          ) : null}
          {section === "dev" ? (
            <ProfileDevSection
              profilDev={profile.profil_dev}
              isOwnProfile={isOwnProfile}
              photo={photo}
            />
          ) : null}
          {section === "entreprise" ? (
            <ProfileCompanySection
              profilEntreprise={profile.profil_entreprise}
              isOwnProfile={isOwnProfile}
              onCreated={() => void refetchProfile()}
            />
          ) : null}
        </div>
      </div>

      {isOwnProfile ? (
        <EditProfileDialog
          open={editOpen}
          onOpenChange={setEditOpen}
          onUpdated={() => void refetchProfile()}
          // Un nouveau nom d'utilisateur change l'adresse du profil
          onUsernameChanged={(username) =>
            navigate(profilePath(username), { replace: true })
          }
        />
      ) : null}
    </div>
  );
}

function FollowProfileButton({
  userId,
  isFollowing,
}: {
  userId: number;
  isFollowing: boolean;
}) {
  const [toggleSuivre, { isLoading }] = useToggleSuivreMembreMutation();

  const handleClick = async () => {
    try {
      const result = await toggleSuivre(userId).unwrap();
      toast.success(
        result.following ? "Tu suis ce membre" : "Tu ne suis plus ce membre"
      );
    } catch {
      toast.error("Impossible de mettre à jour le suivi");
    }
  };

  return (
    <Button
      type="button"
      variant={isFollowing ? "outline" : "default"}
      disabled={isLoading}
      onClick={() => void handleClick()}
    >
      {isFollowing ? "Ne plus suivre" : "Suivre"}
    </Button>
  );
}

function MessageProfileButton({ userId }: { userId: number }) {
  const navigate = useNavigate();
  const [openConversation, { isLoading }] = useOpenConversationMutation();

  const handleClick = async () => {
    try {
      const conversation = await openConversation(userId).unwrap();
      navigate(`/messages/${conversation.id}`);
    } catch {
      toast.error("Impossible d'ouvrir la conversation");
    }
  };

  return (
    <Button type="button" disabled={isLoading} onClick={() => void handleClick()}>
      <Mail className="mr-2 h-4 w-4" />
      Message
    </Button>
  );
}

function ProfilePublications({
  userId,
  isOwnProfile,
}: {
  userId: number;
  isOwnProfile: boolean;
}) {
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const {
    data,
    isLoading,
    isFetching,
    isFetchingNextPage,
    isError,
    refetch,
    fetchNextPage,
    hasNextPage,
  } = useGetPublicationsInfiniteQuery({
    page_size: PAGE_SIZE,
    auteur: userId,
  });

  const results = useMemo(
    () => data?.pages.flatMap((page) => page.results) ?? [],
    [data?.pages]
  );

  useEffect(() => {
    const node = loadMoreRef.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (
          entry?.isIntersecting &&
          hasNextPage &&
          !isFetchingNextPage &&
          !isFetching
        ) {
          void fetchNextPage();
        }
      },
      { rootMargin: "240px 0px" }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetching, isFetchingNextPage]);

  return (
    <div className="space-y-4">
      {isOwnProfile ? (
        <FeedComposer
          onCreated={() => {
            void refetch();
          }}
        />
      ) : null}

      {isLoading ? (
        <p className="rounded-2xl border border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground">
          Chargement des publications…
        </p>
      ) : null}

      {isError ? (
        <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-center">
          <p className="mb-3 text-sm text-destructive">
            Impossible de charger les publications.
          </p>
          <Button type="button" variant="outline" onClick={() => void refetch()}>
            Réessayer
          </Button>
        </div>
      ) : null}

      {!isLoading && !isError && results.length === 0 ? (
        <p className="rounded-2xl border border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
          Aucune publication pour le moment.
        </p>
      ) : null}

      {results.map((publication) => (
        <PublicationCard key={publication.id} publication={publication} />
      ))}

      <div ref={loadMoreRef} className="h-4" />
      {isFetchingNextPage ? (
        <p className="pb-4 text-center text-xs text-muted-foreground">
          Chargement…
        </p>
      ) : null}
    </div>
  );
}

function ProfileProjects({ userId }: { userId: number }) {
  const { data, isLoading, isError } = useGetProjectsQuery({
    owner: userId,
    page: 1,
    page_size: 20,
  });
  const projects = data?.results ?? [];

  if (isLoading) {
    return (
      <p className="rounded-2xl border border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground">
        Chargement des projets…
      </p>
    );
  }

  if (isError) {
    return (
      <p className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-center text-sm text-destructive">
        Impossible de charger les projets.
      </p>
    );
  }

  if (projects.length === 0) {
    return (
      <p className="rounded-2xl border border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
        Aucun projet publié.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {projects.map((project) => (
        <Link
          key={project.id}
          to={`/hub/projects/${project.id}`}
          className="block rounded-2xl border border-border bg-card p-4 shadow-sm transition-colors hover:bg-muted/40"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="truncate font-semibold text-foreground">
                {project.title}
              </h3>
              <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
                {project.problem || project.description || "Sans description"}
              </p>
            </div>
            <span className="shrink-0 rounded-full border border-border px-2 py-0.5 text-[11px] text-muted-foreground">
              {project.status}
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}

function ProfileContributions({ userId }: { userId: number }) {
  const { data, isLoading, isError } = useGetContributionsQuery({
    author_id: userId,
    page: 1,
    page_size: 20,
  });
  const contributions = data?.results ?? [];

  if (isLoading) {
    return (
      <p className="rounded-2xl border border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground">
        Chargement des contributions…
      </p>
    );
  }

  if (isError) {
    return (
      <p className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-center text-sm text-destructive">
        Impossible de charger les contributions.
      </p>
    );
  }

  if (contributions.length === 0) {
    return (
      <p className="rounded-2xl border border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
        Aucune contribution pour le moment.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {contributions.map((item) => (
        <div
          key={item.id}
          className="rounded-2xl border border-border bg-card p-4 shadow-sm"
        >
          <p className="text-sm font-medium text-foreground">
            {item.summary || `Contribution #${item.id}`}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {item.status}
            {item.project_id ? ` · projet #${item.project_id}` : ""}
            {item.created_at
              ? ` · ${new Date(item.created_at).toLocaleDateString("fr-FR")}`
              : ""}
          </p>
        </div>
      ))}
    </div>
  );
}
