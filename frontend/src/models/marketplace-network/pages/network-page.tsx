import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Building2, ChevronUp, Code2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { profilePath } from "@/helpers/routes/profile-path";
import { cn } from "@/lib/utils";
import { formatDate } from "@/models/marketplace-offers/labels";
import type { TalentCard } from "@/models/marketplace-offers/schema";
import { RequireMarketplaceMember } from "@/models/marketplace-space/components/guards";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { useStats } from "@/models/marketplace-stats/api";
import {
  useGetConnectionsQuery,
  useGetDeckQuery,
  useGetNetworkRequestsQuery,
  useSwipeMutation,
  useUndoSwipeMutation,
} from "../api";
import { SwipeDeck, type CardFacts } from "../components/swipe-deck";
import type { ActingAs, DeckCard, NetworkRequest } from "../schema";

function useDescribeCard() {
  const { t } = useTranslation();
  return (card: DeckCard): CardFacts => {
    if (card.type === "entreprise") {
      return {
        k1: t("marketplace.network.type_company"),
        v1: card.company?.name ?? "—",
        k2: t("marketplace.network.city"),
        v2: card.city || card.country,
        proof: card.company?.is_verified
          ? t("marketplace.network.company_verified_proof")
          : t("marketplace.network.company_on_devstreet"),
        source: t("marketplace.network.company_source"),
      };
    }
    const common = card.common_skills ?? [];
    return {
      k1: t("marketplace.network.in_common"),
      v1:
        common.length > 0
          ? t("marketplace.network.skills_count", { count: common.length })
          : t("marketplace.network.skills_none"),
      k2: t("marketplace.network.city"),
      v2: card.city || card.country,
      proof:
        common.length > 0
          ? t("marketplace.network.shared_skills", { list: common.join(", ") })
          : t("marketplace.network.years_exp_short", {
              count: card.years_of_experience,
            }),
      source: t("marketplace.network.dev_source"),
    };
  };
}

/** Choix du profil avec lequel on agit dans le réseau (pour un membre qui a un profil dev et un profil entreprise). */
function ActingSwitch({ value, onChange }: { value: ActingAs; onChange: (value: ActingAs) => void }) {
  const { t } = useTranslation();
  const options: { id: ActingAs; label: string; icon: typeof Code2 }[] = [
    { id: "dev", label: t("marketplace.network.type_dev"), icon: Code2 },
    {
      id: "entreprise",
      label: t("marketplace.network.type_company"),
      icon: Building2,
    },
  ];
  return (
    <div className="mx-auto flex flex-col items-center gap-1.5">
      <span className="text-xs text-muted-foreground">
        {t("marketplace.network.act_as")}
      </span>
      <div
        role="group"
        aria-label={t("marketplace.network.act_as_aria")}
        className="inline-flex rounded-xl border border-brand-soft-border bg-card p-1 shadow-sm"
      >
        {options.map(({ id, label, icon: Icon }) => (
          <Button
            key={id}
            type="button"
            size="sm"
            variant="ghost"
            aria-pressed={value === id}
            onClick={() => onChange(id)}
            className={cn(
              "h-8 gap-1.5 rounded-lg px-3",
              value === id
                ? "bg-brand-soft text-brand-strong hover:bg-brand-soft"
                : "text-muted-foreground"
            )}
          >
            <Icon className="size-4" aria-hidden />
            {label}
          </Button>
        ))}
      </div>
    </div>
  );
}

/** Cellule « membre » des tableaux : initiales, nom (lien vers sa page de profil) et type de profil. */
function MemberCell({ member }: { member: TalentCard }) {
  const { t } = useTranslation();
  const isCompany = member.type === "entreprise";
  return (
    <div className="flex min-w-0 items-center gap-3">
      <ProfileInitialsAvatar
        name={member.name}
        kind={isCompany ? "entreprise" : "dev"}
        openToWork={!isCompany && member.is_open_to_work}
        size="md"
      />
      <div className="flex min-w-0 flex-col">
        {member.username ? (
          <Link
            to={profilePath(member.username, isCompany ? "entreprise" : "dev")}
            className="truncate text-sm font-medium text-foreground hover:underline"
          >
            {member.name}
          </Link>
        ) : (
          <span className="truncate text-sm font-medium text-foreground">
            {member.name}
          </span>
        )}
        <span className="truncate text-xs text-muted-foreground">
          {isCompany
            ? (member.company?.name ?? t("marketplace.network.type_company"))
            : member.headline || t("marketplace.network.type_dev")}
        </span>
      </div>
    </div>
  );
}

function TypeBadge({ member }: { member: TalentCard }) {
  const { t } = useTranslation();
  const isCompany = member.type === "entreprise";
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1",
        isCompany
          ? "border-brand bg-brand-soft text-brand-strong"
          : "border-border text-muted-foreground"
      )}
    >
      {isCompany ? (
        <Building2 className="size-3" aria-hidden />
      ) : (
        <Code2 className="size-3" aria-hidden />
      )}
      {isCompany
        ? t("marketplace.network.type_company")
        : t("marketplace.network.type_dev")}
    </Badge>
  );
}

/** Contenu d'un onglet du panneau : le tableau, un chargement ou un message quand il est vide. */
function TableSection({
  count,
  empty,
  isLoading,
  children,
}: {
  count: number;
  empty: string;
  isLoading: boolean;
  children: ReactNode;
}) {
  if (isLoading) return <Skeleton className="h-16 w-full" />;
  if (count === 0) {
    return (
      <p className="rounded-lg border border-dashed border-border px-4 py-5 text-sm text-muted-foreground">
        {empty}
      </p>
    );
  }
  return <div className="rounded-lg border border-border">{children}</div>;
}

function ConnectionsTable() {
  const { t } = useTranslation();
  const { data, isLoading } = useGetConnectionsQuery();
  const rows = data ?? [];
  return (
    <TableSection
      count={rows.length}
      isLoading={isLoading}
      empty={t("marketplace.network.empty_connections")}
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t("marketplace.network.col_member")}</TableHead>
            <TableHead>{t("marketplace.network.col_type")}</TableHead>
            <TableHead>{t("marketplace.network.col_connected_on")}</TableHead>
            <TableHead className="text-right">
              {t("marketplace.network.col_contact")}
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell>
                <MemberCell member={row} />
              </TableCell>
              <TableCell>
                <TypeBadge member={row} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(row.matched_at)}
              </TableCell>
              <TableCell className="text-right">
                {row.email ? (
                  <Button asChild size="sm" variant="outline">
                    <a href={`mailto:${row.email}`}>
                      {t("marketplace.network.write_them")}
                    </a>
                  </Button>
                ) : null}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableSection>
  );
}

function PendingTable({ rows, isLoading }: { rows: NetworkRequest[]; isLoading: boolean }) {
  const { t } = useTranslation();
  return (
    <TableSection
      count={rows.length}
      isLoading={isLoading}
      empty={t("marketplace.network.empty_pending")}
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t("marketplace.network.col_member")}</TableHead>
            <TableHead>{t("marketplace.network.col_type")}</TableHead>
            <TableHead>{t("marketplace.network.col_sent_on")}</TableHead>
            <TableHead className="text-right">
              {t("marketplace.network.col_status")}
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell>
                <MemberCell member={row} />
              </TableCell>
              <TableCell>
                <TypeBadge member={row} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(row.requested_at)}
              </TableCell>
              <TableCell className="text-right text-xs text-muted-foreground">
                {t("marketplace.network.pending_status")}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableSection>
  );
}

function ReceivedTable({
  rows,
  isLoading,
  onAnswered,
}: {
  rows: NetworkRequest[];
  isLoading: boolean;
  onAnswered: () => void;
}) {
  const { t } = useTranslation();
  const [swipe, { isLoading: answering }] = useSwipeMutation();

  const answer = async (row: NetworkRequest, direction: "like" | "pass") => {
    try {
      const result = await swipe({
        target_id: row.id,
        direction,
        context: "network",
        acting: row.acting,
      }).unwrap();
      if (direction === "like" && result.matched) {
        CreationSuccessSonner(
          t("marketplace.network.matched", { name: row.name })
        );
      }
      onAnswered();
    } catch {
      CreationErrorSonner(t("marketplace.network.answer_error"));
    }
  };

  return (
    <TableSection
      count={rows.length}
      isLoading={isLoading}
      empty={t("marketplace.network.empty_received")}
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t("marketplace.network.col_member")}</TableHead>
            <TableHead>{t("marketplace.network.col_type")}</TableHead>
            <TableHead>{t("marketplace.network.col_received_on")}</TableHead>
            <TableHead className="text-right">
              {t("marketplace.network.col_reply")}
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell>
                <MemberCell member={row} />
              </TableCell>
              <TableCell>
                <TypeBadge member={row} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(row.requested_at)}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    size="sm"
                    disabled={answering}
                    onClick={() => void answer(row, "like")}
                  >
                    {t("marketplace.network.accept")}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={answering}
                    onClick={() => void answer(row, "pass")}
                  >
                    {t("marketplace.network.decline")}
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableSection>
  );
}

type PanelTab = "connections" | "pending" | "received";

/** Panneau qui monte du bas, avec un onglet par liste : connexions, demandes en attente, demandes reçues. */
function NetworkPanel({
  open,
  onOpenChange,
  onAnswered,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAnswered: () => void;
}) {
  const { t } = useTranslation();
  const [tab, setTab] = useState<PanelTab>("connections");
  const { data, isLoading } = useGetNetworkRequestsQuery(undefined, { skip: !open });
  const { data: connections } = useGetConnectionsQuery(undefined, { skip: !open });
  const received = data?.received ?? [];

  const tabs: {
    id: PanelTab;
    label: string;
    count: number | undefined;
    accent?: boolean;
  }[] = [
    {
      id: "connections",
      label: t("marketplace.network.tab_connections"),
      count: connections?.length,
    },
    {
      id: "pending",
      label: t("marketplace.network.tab_pending"),
      count: data?.sent.length,
    },
    {
      id: "received",
      label: t("marketplace.network.tab_received"),
      count: data?.received.length,
      accent: received.length > 0,
    },
  ];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="bottom"
        className="mx-auto max-h-[85vh] w-full max-w-4xl overflow-y-auto rounded-t-2xl"
      >
        <SheetHeader className="mb-3 text-left">
          <SheetTitle>{t("marketplace.network.panel_title")}</SheetTitle>
          <SheetDescription className="sr-only">
            {t("marketplace.network.panel_desc")}
          </SheetDescription>
        </SheetHeader>

        <div
          role="tablist"
          aria-label={t("marketplace.network.panel_title")}
          className="mb-4 flex gap-1 overflow-x-auto border-b border-border"
        >
          {tabs.map((item) => {
            const selected = tab === item.id;
            return (
              <button
                key={item.id}
                id={`network-tab-${item.id}`}
                type="button"
                role="tab"
                aria-selected={selected}
                aria-controls={`network-panel-${item.id}`}
                onClick={() => setTab(item.id)}
                className={cn(
                  "-mb-px flex shrink-0 items-center gap-2 border-b-2 px-3 py-2 text-sm font-medium transition-colors",
                  selected
                    ? "border-brand text-brand-strong"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                )}
              >
                {item.label}
                {item.count !== undefined ? (
                  <Badge
                    variant={item.accent && !selected ? "default" : "secondary"}
                    className={cn(
                      item.accent && !selected && "bg-brand text-brand-foreground"
                    )}
                  >
                    {item.count}
                  </Badge>
                ) : null}
              </button>
            );
          })}
        </div>

        <div
          role="tabpanel"
          id={`network-panel-${tab}`}
          aria-labelledby={`network-tab-${tab}`}
          className="pb-4"
        >
          {tab === "connections" ? <ConnectionsTable /> : null}
          {tab === "pending" ? (
            <PendingTable rows={data?.sent ?? []} isLoading={isLoading} />
          ) : null}
          {tab === "received" ? (
            <ReceivedTable
              rows={received}
              isLoading={isLoading}
              onAnswered={onAnswered}
            />
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}

/**
 * Lien sous « Agir en tant que » : assez visible pour être repéré, sans alourdir la page. Une pastille violette
 * signale les demandes reçues auxquelles on n'a pas encore répondu.
 */
function NetworkLink({ onOpen }: { onOpen: () => void }) {
  const { t } = useTranslation();
  const { data } = useStats("network");
  const received = data?.pending_received ?? 0;

  return (
    <button
      type="button"
      onClick={onOpen}
      aria-haspopup="dialog"
      className="mx-auto inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-brand-strong underline-offset-4 transition-colors hover:bg-brand-soft hover:underline"
    >
      {t("marketplace.network.see_my_network")}
      <ChevronUp className="size-4" aria-hidden />
      {received > 0 ? (
        <span
          className="rounded-full bg-brand px-2 py-0.5 text-xs font-semibold leading-none text-brand-foreground"
          aria-label={t("marketplace.network.received_aria", {
            count: received,
          })}
        >
          {received}
        </span>
      ) : null}
    </button>
  );
}

function NetworkContent() {
  const { t } = useTranslation();
  const describe = useDescribeCard();
  const { hasProfil, isRecruiter } = useMySpace();
  // Un membre qui a les deux profils choisit avec lequel il agit ; sinon le serveur prend son seul profil
  const hasBoth = hasProfil && isRecruiter;
  const [choice, setChoice] = useState<ActingAs>("dev");
  const acting: ActingAs | undefined = hasBoth ? choice : undefined;
  const [panelOpen, setPanelOpen] = useState(false);
  // Repart d'un paquet neuf quand on répond à une demande depuis le panneau (la personne ne doit plus y figurer)
  const [deckVersion, setDeckVersion] = useState(0);

  const { data, isLoading, isError, refetch } = useGetDeckQuery(
    { context: "network", acting },
    { refetchOnMountOrArgChange: true }
  );
  const [swipe] = useSwipeMutation();
  const [undo] = useUndoSwipeMutation();

  const handleAnswered = async () => {
    await refetch();
    setDeckVersion((version) => version + 1);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-center gap-2">
        {hasBoth ? <ActingSwitch value={choice} onChange={setChoice} /> : null}
        <NetworkLink onOpen={() => setPanelOpen(true)} />
      </div>

      {isLoading ? (
        <Skeleton className="mx-auto h-96 w-full max-w-md" />
      ) : isError || !data ? (
        <p className="mx-auto max-w-md rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          {t("marketplace.network.load_error")}
        </p>
      ) : (
        <SwipeDeck
          // Le paquet repart de zéro quand on change de profil ou après une réponse depuis le panneau
          key={`${acting ?? "auto"}-${deckVersion}`}
          cards={data}
          title={t("marketplace.network.title")}
          hideHeader
          likeVerb={t("marketplace.network.like_verb")}
          likeStamp={t("marketplace.network.like_stamp")}
          likeAria={t("marketplace.network.like_aria")}
          describe={describe}
          matchedText={(name) =>
            t("marketplace.network.matched_text", { name })
          }
          matchedAction={
            <Button onClick={() => setPanelOpen(true)}>
              {t("marketplace.network.see_connections")}
            </Button>
          }
          emptyAction={
            <Badge variant="secondary">
              {t("marketplace.network.come_back_tomorrow")}
            </Badge>
          }
          onSwipe={async (card, direction) => {
            try {
              return await swipe({
                target_id: card.id,
                direction,
                context: "network",
                acting,
              }).unwrap();
            } catch {
              CreationErrorSonner(t("marketplace.swipe_error"));
              return null;
            }
          }}
          onUndo={async () => {
            try {
              await undo({ context: "network", acting }).unwrap();
              return true;
            } catch {
              CreationErrorSonner(t("marketplace.undo_error"));
              return false;
            }
          }}
        />
      )}

      <NetworkPanel
        open={panelOpen}
        onOpenChange={setPanelOpen}
        onAnswered={() => void handleAnswered()}
      />
    </div>
  );
}

/** Réseau : ouvert aux devs comme aux entreprises. Un like réciproque crée une connexion. */
export default function NetworkPage() {
  return (
    <RequireMarketplaceMember>
      <NetworkContent />
    </RequireMarketplaceMember>
  );
}
