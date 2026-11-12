import { useState } from "react";
import { RelationSelect } from "@/components/relation-select/relation-select";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import type { RelationRef } from "@/helpers/api/relations";
import { useGetProfilsQuery } from "../api";
import type { GetProfilSchema } from "../schema";

type ProfilSelectProps = {
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  /** Relation déjà liée (édition), pour afficher son libellé immédiatement. */
  selectedItem?: RelationRef | null;
  clearable?: boolean;
  disabled?: boolean;
};

const profilLabel = (item: GetProfilSchema): string =>
  [item.slug, item.headline].filter(Boolean).join(" — ") || `#${item.id}`;

/** Sélecteur de un profil (recherche côté serveur). */
export function ProfilSelect({
  value,
  onChange,
  selectedItem,
  clearable,
  disabled,
}: ProfilSelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data, isFetching } = useGetProfilsQuery({
    search: debouncedSearch,
    page_size: 20,
  });

  return (
    <RelationSelect<GetProfilSchema>
      value={value}
      onChange={onChange}
      items={data?.results ?? []}
      getLabel={profilLabel}
      onSearchChange={setSearch}
      isLoading={isFetching}
      selectedItem={selectedItem as unknown as GetProfilSchema | null | undefined}
      placeholder="Sélectionner un profil..."
      clearable={clearable}
      disabled={disabled}
    />
  );
}
