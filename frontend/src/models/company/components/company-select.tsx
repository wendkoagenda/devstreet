import { useState } from "react";
import { RelationSelect } from "@/components/relation-select/relation-select";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import type { RelationRef } from "@/helpers/api/relations";
import { useGetCompaniesQuery } from "../api";
import type { GetCompanySchema } from "../schema";

type CompanySelectProps = {
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  /** Relation déjà liée (édition), pour afficher son libellé immédiatement. */
  selectedItem?: RelationRef | null;
  clearable?: boolean;
  disabled?: boolean;
};

const companyLabel = (item: GetCompanySchema): string =>
  item.name || `#${item.id}`;

/** Sélecteur de une entreprise (recherche côté serveur). */
export function CompanySelect({
  value,
  onChange,
  selectedItem,
  clearable,
  disabled,
}: CompanySelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const { data, isFetching } = useGetCompaniesQuery({
    search: debouncedSearch,
    page_size: 20,
  });

  return (
    <RelationSelect<GetCompanySchema>
      value={value}
      onChange={onChange}
      items={data?.results ?? []}
      getLabel={companyLabel}
      onSearchChange={setSearch}
      isLoading={isFetching}
      selectedItem={selectedItem as unknown as GetCompanySchema | null | undefined}
      placeholder="Sélectionner une entreprise..."
      clearable={clearable}
      disabled={disabled}
    />
  );
}
