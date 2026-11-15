import { profilePath } from "@/helpers/routes/profile-path";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useAuthSlice } from "@/models/auth/slice";
import {
  useQuitterEspaceMutation,
  useRejoindreEspaceMutation,
  useToggleSuivreMembreMutation,
} from "../api";
import type { Espace } from "../schema";
import { ForumAvatar } from "./forum-avatar";

type Peer = {
  id: number;
  username: string;
  full_name: string;
  photo?: string;
  following?: boolean;
};

type FeedIndexAsideProps = {
  peers: Peer[];
  topCommunautes: Espace[];
  topChaines: Espace[];
};

export function FeedIndexAside({
  peers,
  topCommunautes,
  topChaines,
}: FeedIndexAsideProps) {
  const { t } = useTranslation();
  const currentUserId = useAuthSlice((state) => state.user?.id ?? null);

  return (
    <aside className="space-y-4 xl:sticky xl:top-24 xl:self-start">
      {peers.length > 0 ? (
        <section className="rounded-xl border border-border bg-card p-4 sm:p-5">
          <h2 className="mb-3.5 text-xs font-semibold tracking-wide text-foreground">
            {t("forum.aside_active")}
          </h2>
          <ul className="space-y-3">
            {peers.map((peer) => (
              <li key={peer.id} className="flex items-center gap-2">
                <ForumAvatar
                  name={peer.full_name || peer.username}
                  photo={peer.photo}
                  size="sm"
                  tone="soft"
                />
                <Link
                  to={profilePath(peer.username)}
                  className="min-w-0 flex-1 truncate text-xs font-medium hover:text-brand"
                >
                  {peer.full_name || peer.username}
                </Link>
                <PeerAction
                  peerId={peer.id}
                  currentUserId={currentUserId}
                  following={Boolean(peer.following)}
                />
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <EspaceAsideList
        title={t("forum.aside_top_communities")}
        hrefAll="/forum/communautes"
        items={topCommunautes}
        detailBase="/forum/communautes"
        actionLabel={t("forum.action_join")}
        joinedLabel={t("forum.action_joined_member")}
      />

      <EspaceAsideList
        title={t("forum.aside_top_channels")}
        hrefAll="/forum/chaines"
        items={topChaines}
        detailBase="/forum/chaines"
        actionLabel={t("forum.action_follow")}
        joinedLabel={t("forum.action_joined_subscriber")}
      />
    </aside>
  );
}

function PeerAction({
  peerId,
  currentUserId,
  following,
}: {
  peerId: number;
  currentUserId: number | null;
  following: boolean;
}) {
  const [toggleSuivre, { isLoading }] = useToggleSuivreMembreMutation();

  const { t } = useTranslation();

  if (currentUserId != null && peerId === currentUserId) {
    return (
      <span className="rounded-md bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
        {t("forum.you")}
      </span>
    );
  }

  if (following) {
    return (
      <span className="rounded-md bg-brand-soft px-2 py-0.5 text-[10px] font-medium text-brand">
        {t("forum.action_following")}
      </span>
    );
  }

  return (
    <Button
      type="button"
      size="sm"
      variant="outline"
      className="h-7 px-2 text-[11px]"
      disabled={isLoading}
      onClick={() => {
        void toggleSuivre(peerId)
          .unwrap()
          .then((result) => {
            toast.success(
              result.following
                ? "Vous suivez ce membre"
                : "Vous ne suivez plus ce membre"
            );
          })
          .catch(() => toast.error("Impossible de mettre à jour le suivi"));
      }}
    >
      {t("forum.action_follow")}
    </Button>
  );
}

function EspaceAsideList({
  title,
  hrefAll,
  items,
  detailBase,
  actionLabel,
  joinedLabel,
}: {
  title: string;
  hrefAll: string;
  items: Espace[];
  detailBase: "/forum/communautes" | "/forum/chaines";
  actionLabel: string;
  joinedLabel: string;
}) {
  if (items.length === 0) return null;

  return (
    <section className="rounded-xl border border-border bg-card p-4 sm:p-5">
      <div className="mb-3.5 flex items-center justify-between gap-2">
        <h2 className="text-xs font-semibold tracking-wide text-foreground">{title}</h2>
        <Link
          to={hrefAll}
          className="text-[11px] font-medium text-brand hover:underline"
        >
          Voir tout
        </Link>
      </div>
      <ul className="space-y-2.5">
        {items.map((espace) => (
          <li key={espace.id} className="flex items-center gap-2">
            <ForumAvatar
              name={espace.nom}
              photo={espace.photo || undefined}
              size="sm"
              tone={espace.type === "CHAINE" ? "brand" : "soft"}
            />
            <div className="min-w-0 flex-1">
              <Link
                to={`${detailBase}/${espace.id}`}
                className="block truncate text-xs font-medium hover:text-brand"
              >
                {espace.nom}
              </Link>
              <p className="font-mono text-[10px] tabular-nums text-muted-foreground">
                {espace.membres_count ?? 0}{" "}
                {espace.type === "CHAINE" ? "abonnés" : "membres"}
              </p>
            </div>
            <EspaceJoinButton
              espace={espace}
              actionLabel={actionLabel}
              joinedLabel={joinedLabel}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

function EspaceJoinButton({
  espace,
  actionLabel,
  joinedLabel,
}: {
  espace: Espace;
  actionLabel: string;
  joinedLabel: string;
}) {
  const [rejoindre, { isLoading: joining }] = useRejoindreEspaceMutation();
  const [quitter, { isLoading: leaving }] = useQuitterEspaceMutation();
  const joined = espace.mon_role != null;
  // Le créateur ne peut pas quitter : pas de bouton inutile.
  if (espace.mon_role === "SUPER_ADMIN") return null;

  if (joined) {
    return (
      <Button
        type="button"
        size="sm"
        variant="ghost"
        className="h-7 px-2 text-[11px] text-muted-foreground"
        disabled={leaving}
        onClick={() => {
          void quitter(espace.id)
            .unwrap()
            .then(() => toast.success("Vous avez quitté cet espace"))
            .catch(() => toast.error("Impossible de quitter"));
        }}
      >
        {joinedLabel}
      </Button>
    );
  }

  return (
    <Button
      type="button"
      size="sm"
      variant="outline"
      className="h-7 px-2 text-[11px]"
      disabled={joining}
      onClick={() => {
        void rejoindre(espace.id)
          .unwrap()
          .then(() => toast.success(`${actionLabel} — c’est fait`))
          .catch(() => toast.error(`Impossible de ${actionLabel.toLowerCase()}`));
      }}
    >
      {actionLabel}
    </Button>
  );
}
