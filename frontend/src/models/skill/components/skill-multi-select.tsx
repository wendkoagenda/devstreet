import { MultiSelect } from "@/components/ui/multi-select";
import { useGetSkillsQuery } from "../api";

type SkillMultiSelectProps = {
  /** Identifiants des compétences sélectionnées. */
  value: number[];
  onChange: (value: number[]) => void;
};

/** Sélection multiple de compétences (relation M2M), sur les 100 premières compétences. */
export function SkillMultiSelect({ value, onChange }: SkillMultiSelectProps) {
  const { data } = useGetSkillsQuery({ page_size: 100 });
  const options = (data?.results ?? []).map((skill) => ({
    value: String(skill.id),
    label: skill.name || `#${skill.id}`,
  }));

  return (
    <MultiSelect
      options={options}
      selected={value.map(String)}
      onChange={(selected) => onChange(selected.map(Number))}
      placeholder="Sélectionner des compétences..."
    />
  );
}
