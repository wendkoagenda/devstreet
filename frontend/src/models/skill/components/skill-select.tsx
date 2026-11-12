import { useState } from "react";
import { RelationSelect } from "@/components/relation-select/relation-select";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import type { RelationRef } from "@/helpers/api/relations";
import { useGetSkillsQuery } from "../api";
import type { GetSkillSchema } from "../schema";

type SkillSelectProps = {
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  /** Relation déjà liée (édition), pour afficher son libellé immédiatement. */
  selectedItem?: RelationRef | null;
  clearable?: boolean;
  disabled?: boolean;
};

const skillLabel = (item: GetSkillSchema): string =>
  item.name || `#${item.id}`;

/** Sélecteur de une compétence (recherche côté serveur). */
export function SkillSelect({
  value,
  onChange,
  selectedItem,
  clearable,
  disabled,
}: SkillSelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data, isFetching } = useGetSkillsQuery({
    search: debouncedSearch,
    page_size: 20,
  });

  return (
    <RelationSelect<GetSkillSchema>
      value={value}
      onChange={onChange}
      items={data?.results ?? []}
      getLabel={skillLabel}
      onSearchChange={setSearch}
      isLoading={isFetching}
      selectedItem={selectedItem as unknown as GetSkillSchema | null | undefined}
      placeholder="Sélectionner une compétence..."
      clearable={clearable}
      disabled={disabled}
    />
  );
}
