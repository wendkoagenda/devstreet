import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { formatDate } from "@/models/marketplace-offers/labels";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useGetDeckQuery, useSwipeMutation, useUndoSwipeMutation } from "../api";
import { SwipeDeck, type CardFacts } from "../components/swipe-deck";
import type { DeckCard } from "../schema";

function useDescribeCard() {
  const { t } = useTranslation();
  return (card: DeckCard): CardFacts => {
    const rating =
      card.rating_avg !== null
        ? t("marketplace.rating_avg", {
            avg: card.rating_avg,
            count: card.reviews_count,
          })
        : "";
    return {
      k1: t("marketplace.available_label"),
      v1: card.available_from
        ? t("marketplace.available_from", { date: formatDate(card.available_from) })
        : t("marketplace.available_tbd"),
      k2: t("marketplace.score_label"),
      v2:
        card.score !== null
          ? `${card.score} / 100`
          : t("marketplace.no_open_offer"),
      proof: `${t("marketplace.years_exp", { count: card.years_of_experience })}${rating}.`,
      source: t("marketplace.reco_source"),
    };
  };
}

function TalentsDiscoverContent() {
  const { t } = useTranslation();
  const describe = useDescribeCard();
  const { data, isLoading, isError } = useGetDeckQuery(
    { context: "recruit" },
    { refetchOnMountOrArgChange: true }
  );
  const [swipe] = useSwipeMutation();
  const [undo] = useUndoSwipeMutation();

  if (isLoading) return <Skeleton className="mx-auto h-96 w-full max-w-md" />;
  if (isError || !data) {
    return (
      <p className="mx-auto max-w-md rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
        {t("marketplace.load_profiles_error")}
      </p>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Button asChild variant="outline" size="sm">
          <Link to="/marketplace/talents">{t("marketplace.back_to_directory")}</Link>
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link to="/marketplace/talents/pool">{t("marketplace.pool")}</Link>
        </Button>
      </div>
      <SwipeDeck
        cards={data}
        title={t("marketplace.discover_profiles")}
        likeVerb={t("marketplace.like_verb")}
        likeStamp={t("marketplace.like_stamp")}
        likeAria={t("marketplace.like_aria")}
        keptLabel={(kept) => t("marketplace.pool_kept", { count: kept })}
        describe={describe}
        matchedText={(name) => name}
        emptyAction={
          <Button asChild>
            <Link to="/marketplace/talents/pool">{t("marketplace.see_pool")}</Link>
          </Button>
        }
        onSwipe={async (card, direction) => {
          try {
            return await swipe({ target_id: card.id, direction, context: "recruit" }).unwrap();
          } catch {
            CreationErrorSonner(t("marketplace.swipe_error"));
            return null;
          }
        }}
        onUndo={async () => {
          try {
            await undo({ context: "recruit" }).unwrap();
            return true;
          } catch {
            CreationErrorSonner(t("marketplace.undo_error"));
            return false;
          }
        }}
      />
    </div>
  );
}

/** Mode swipe : constituer le vivier sans filtres (complément de l'annuaire UC-08). */
export default function TalentsDiscoverPage() {
  return (
    <RequireRecruiter>
      <TalentsDiscoverContent />
    </RequireRecruiter>
  );
}
