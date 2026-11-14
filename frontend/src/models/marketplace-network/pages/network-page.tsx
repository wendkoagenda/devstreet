import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { useState, type ReactNode } from "react";
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

function describe(card: DeckCard): CardFacts {
  if (card.type === "entreprise") {
    return {
      k1: "Entreprise",
      v1: card.company?.name ?? "—",
      k2: "Ville",
      v2: card.city || card.country,
      proof: card.company?.is_verified ? "Entreprise vérifiée." : "Entreprise présente sur DevStreet.",
      source: "Profil entreprise du réseau",
    };
  }
  const common = card.common_skills ?? [];
  return {
    k1: "En commun",
    v1: common.length > 0 ? `${common.length} compétence(s)` : "Aucune pour l'instant",
    k2: "Ville",
    v2: card.city || card.country,
    proof:
      common.length > 0
        ? `Compétences partagées : ${common.join(", ")}.`
        : `${card.years_of_experience} an(s) d'expérience.`,
    source: "Dev proche de vous : compétences et ville en commun",
  };
}

/** Choix du profil avec lequel on agit dans le réseau (pour un membre qui a un profil dev et un profil entreprise). */
function ActingSwitch({ value, onChange }: { value: ActingAs; onChange: (value: ActingAs) => void }) {
  const options: { id: ActingAs; label: string; icon: typeof Code2 }[] = [
    { id: "dev", label: "Dev", icon: Code2 },
    { id: "entreprise", label: "Entreprise", icon: Building2 },
  ];
  return (
    <div className="mx-auto flex flex-col items-center gap-1.5">
      <span className="text-xs text-muted-foreground">Agir en tant que</span>
      <div
        role="group"
        aria-label="Profil utilisé dans le réseau"
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
              value === id ? "bg-brand-soft text-brand-strong hover:bg-brand-soft" : "text-muted-foreground"
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
          <span className="truncate text-sm font-medium text-foreground">{member.name}</span>
        )}
        <span className="truncate text-xs text-muted-foreground">
          {isCompany ? (member.company?.name ?? "Entreprise") : member.headline || "Dev"}
        </span>
      </div>
    </div>
  );
}

function TypeBadge({ member }: { member: TalentCard }) {
  const isCompany = member.type === "entreprise";
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1",
        isCompany ? "border-brand bg-brand-soft text-brand-strong" : "border-border text-muted-foreground"
      )}
    >
      {isCompany ? <Building2 className="size-3" aria-hidden /> : <Code2 className="size-3" aria-hidden />}
      {isCompany ? "Entreprise" : "Dev"}
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
  const { data, isLoading } = useGetConnectionsQuery();
  const rows = data ?? [];
  return (
    <TableSection
      count={rows.length}
      isLoading={isLoading}
      empty="Pas encore de connexion : quand deux membres, devs ou entreprises, se choisissent mutuellement, ils apparaissent ici."
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Membre</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Connectés le</TableHead>
            <TableHead className="text-right">Contact</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell><MemberCell member={row} /></TableCell>
              <TableCell><TypeBadge member={row} /></TableCell>
              <TableCell className="text-muted-foreground">{formatDate(row.matched_at)}</TableCell>
              <TableCell className="text-right">
                {row.email ? (
                  <Button asChild size="sm" variant="outline">
                    <a href={`mailto:${row.email}`}>Lui écrire</a>
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
  return (
    <TableSection
      count={rows.length}
      isLoading={isLoading}
      empty="Aucune demande en attente : celles que vous envoyez apparaissent ici jusqu'à la réponse."
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Membre</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Envoyée le</TableHead>
            <TableHead className="text-right">Statut</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell><MemberCell member={row} /></TableCell>
              <TableCell><TypeBadge member={row} /></TableCell>
              <TableCell className="text-muted-foreground">{formatDate(row.requested_at)}</TableCell>
              <TableCell className="text-right text-xs text-muted-foreground">En attente de réponse</TableCell>
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
        CreationSuccessSonner(`Vous êtes maintenant connecté avec ${row.name}`);
      }
      onAnswered();
    } catch {
      CreationErrorSonner("Impossible d'enregistrer votre réponse");
    }
  };

  return (
    <TableSection
      count={rows.length}
      isLoading={isLoading}
      empty="Aucune demande reçue pour le moment."
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Membre</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Reçue le</TableHead>
            <TableHead className="text-right">Réponse</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell><MemberCell member={row} /></TableCell>
              <TableCell><TypeBadge member={row} /></TableCell>
              <TableCell className="text-muted-foreground">{formatDate(row.requested_at)}</TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-2">
                  <Button type="button" size="sm" disabled={answering} onClick={() => void answer(row, "like")}>
                    Accepter
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={answering}
                    onClick={() => void answer(row, "pass")}
                  >
                    Refuser
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
  const [tab, setTab] = useState<PanelTab>("connections");
  const { data, isLoading } = useGetNetworkRequestsQuery(undefined, { skip: !open });
  const { data: connections } = useGetConnectionsQuery(undefined, { skip: !open });
  const received = data?.received ?? [];

  const tabs: { id: PanelTab; label: string; count: number | undefined; accent?: boolean }[] = [
    { id: "connections", label: "Connexions", count: connections?.length },
    { id: "pending", label: "Demandes en attente", count: data?.sent.length },
    { id: "received", label: "Demandes reçues", count: data?.received.length, accent: received.length > 0 },
  ];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="mx-auto max-h-[85vh] w-full max-w-4xl overflow-y-auto rounded-t-2xl">
        <SheetHeader className="mb-3 text-left">
          <SheetTitle>Mon réseau</SheetTitle>
          <SheetDescription className="sr-only">
            Vos connexions, les demandes que vous avez envoyées et celles que vous avez reçues.
          </SheetDescription>
        </SheetHeader>

        <div role="tablist" aria-label="Mon réseau" className="mb-4 flex gap-1 overflow-x-auto border-b border-border">
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
                    className={cn(item.accent && !selected && "bg-brand text-brand-foreground")}
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
          {tab === "pending" ? <PendingTable rows={data?.sent ?? []} isLoading={isLoading} /> : null}
          {tab === "received" ? (
            <ReceivedTable rows={received} isLoading={isLoading} onAnswered={onAnswered} />
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
  const { data } = useStats("network");
  const received = data?.pending_received ?? 0;

  return (
    <button
      type="button"
      onClick={onOpen}
      aria-haspopup="dialog"
      className="mx-auto inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-brand-strong underline-offset-4 transition-colors hover:bg-brand-soft hover:underline"
    >
      Voir mon réseau
      <ChevronUp className="size-4" aria-hidden />
      {received > 0 ? (
        <span
          className="rounded-full bg-brand px-2 py-0.5 text-xs font-semibold leading-none text-brand-foreground"
          aria-label={`${received} demande(s) reçue(s)`}
        >
          {received}
        </span>
      ) : null}
    </button>
  );
}

function NetworkContent() {
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
          Impossible de charger les profils. Réessayez dans un instant.
        </p>
      ) : (
        <SwipeDeck
          // Le paquet repart de zéro quand on change de profil ou après une réponse depuis le panneau
          key={`${acting ?? "auto"}-${deckVersion}`}
          cards={data}
          title="Réseau"
          hideHeader
          likeVerb="proposer de se connecter"
          likeStamp="Connexion"
          likeAria="Se connecter"
          describe={describe}
          matchedText={(name) =>
            `${name} souhaite aussi se connecter avec vous. Vous pouvez maintenant échanger.`
          }
          matchedAction={<Button onClick={() => setPanelOpen(true)}>Voir mes connexions</Button>}
          emptyAction={<Badge variant="secondary">Revenez demain</Badge>}
          onSwipe={async (card, direction) => {
            try {
              return await swipe({
                target_id: card.id,
                direction,
                context: "network",
                acting,
              }).unwrap();
            } catch {
              CreationErrorSonner("Impossible d'enregistrer ce choix");
              return null;
            }
          }}
          onUndo={async () => {
            try {
              await undo({ context: "network", acting }).unwrap();
              return true;
            } catch {
              CreationErrorSonner("Impossible d'annuler le dernier choix");
              return false;
            }
          }}
        />
      )}

      <NetworkPanel open={panelOpen} onOpenChange={setPanelOpen} onAnswered={() => void handleAnswered()} />
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
