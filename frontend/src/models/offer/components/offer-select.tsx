import { useState } from "react";
import { RelationSelect } from "@/components/relation-select/relation-select";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import type { RelationRef } from "@/helpers/api/relations";
import { useGetOffersQuery } from "../api";
import type { GetOfferSchema } from "../schema";

type OfferSelectProps = {
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  /** Relation déjà liée (édition), pour afficher son libellé immédiatement. */
  selectedItem?: RelationRef | null;
  clearable?: boolean;
  disabled?: boolean;
};

const offerLabel = (item: GetOfferSchema): string =>
  item.title || `#${item.id}`;

/** Sélecteur de une offre (recherche côté serveur). */
export function OfferSelect({
  value,
  onChange,
  selectedItem,
  clearable,
  disabled,
}: OfferSelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data, isFetching } = useGetOffersQuery({
    search: debouncedSearch,
    page_size: 20,
  });

  return (
    <RelationSelect<GetOfferSchema>
      value={value}
      onChange={onChange}
      items={data?.results ?? []}
      getLabel={offerLabel}
      onSearchChange={setSearch}
      isLoading={isFetching}
      selectedItem={selectedItem as unknown as GetOfferSchema | null | undefined}
      placeholder="Sélectionner une offre..."
      clearable={clearable}
      disabled={disabled}
    />
  );
}
