import { MultiSelect } from "@/components/ui/multi-select";
import { useGetSkillOptionsQuery } from "../api";

type SkillPickerProps = {
  /** Identifiants des compétences choisies. */
  value: number[];
  onChange: (value: number[]) => void;
  placeholder?: string;
};

/** Choix multiple dans le référentiel des compétences (géré par l'administration). */
export function SkillPicker({ value, onChange, placeholder = "Sélectionner des compétences..." }: SkillPickerProps) {
  const { data } = useGetSkillOptionsQuery();
  const options = (data ?? []).map((skill) => ({ value: String(skill.id), label: skill.name }));

  return (
    <MultiSelect
      options={options}
      selected={value.map(String)}
      onChange={(selected) => onChange(selected.map(Number))}
      placeholder={placeholder}
    />
  );
}
