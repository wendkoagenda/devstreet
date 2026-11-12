import { useState } from "react";
import { RelationSelect } from "@/components/relation-select/relation-select";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import type { RelationRef } from "@/helpers/api/relations";
import { useGetCandidaturesQuery } from "../api";
import type { GetCandidatureSchema } from "../schema";

type CandidatureSelectProps = {
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  /** Relation déjà liée (édition), pour afficher son libellé immédiatement. */
  selectedItem?: RelationRef | null;
  clearable?: boolean;
  disabled?: boolean;
};

const candidatureLabel = (item: GetCandidatureSchema): string =>
  `Candidature #${item.id}${item.message ? " — " + String(item.message).slice(0, 40) : ""}`;

/** Sélecteur de une candidature (recherche côté serveur). */
export function CandidatureSelect({
  value,
  onChange,
  selectedItem,
  clearable,
  disabled,
}: CandidatureSelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data, isFetching } = useGetCandidaturesQuery({
    search: debouncedSearch,
    page_size: 20,
  });

  return (
    <RelationSelect<GetCandidatureSchema>
      value={value}
      onChange={onChange}
      items={data?.results ?? []}
      getLabel={candidatureLabel}
      onSearchChange={setSearch}
      isLoading={isFetching}
      selectedItem={selectedItem as unknown as GetCandidatureSchema | null | undefined}
      placeholder="Sélectionner une candidature..."
      clearable={clearable}
      disabled={disabled}
    />
  );
}
