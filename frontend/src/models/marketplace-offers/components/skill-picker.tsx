import { useMemo, useState } from "react";
import { Check, ChevronsUpDown, Plus, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { useGetSkillOptionsQuery } from "../api";

type SkillPickerProps = {
  /** Identifiants des compétences choisies. */
  value: number[];
  onChange: (value: number[]) => void;
  placeholder?: string;
};

/** Choix multiple dans le référentiel des compétences (géré par l'administration). */
export function SkillPicker({
  value,
  onChange,
  placeholder = "Rechercher une compétence à ajouter…",
}: SkillPickerProps) {
  const { data, isLoading, isError } = useGetSkillOptionsQuery();
  const [open, setOpen] = useState(false);

  const options = useMemo(
    () => (data ?? []).map((skill) => ({ id: skill.id, name: skill.name })),
    [data]
  );

  const selected = useMemo(() => {
    const byId = new Map(options.map((skill) => [skill.id, skill.name]));
    return value.map((id) => ({
      id,
      name: byId.get(id) ?? `#${id}`,
    }));
  }, [options, value]);

  const available = useMemo(
    () => options.filter((skill) => !value.includes(skill.id)),
    [options, value]
  );

  const add = (id: number) => {
    if (value.includes(id)) return;
    onChange([...value, id]);
    setOpen(false);
  };

  const remove = (id: number) => {
    onChange(value.filter((skillId) => skillId !== id));
  };

  return (
    <div className="flex flex-col gap-3">
      {selected.length > 0 ? (
        <div className="flex flex-wrap gap-1.5 rounded-lg border border-border bg-muted/30 p-2">
          {selected.map((skill) => (
            <Badge
              key={skill.id}
              variant="secondary"
              className="gap-1 rounded-md px-2 py-1 font-normal"
            >
              {skill.name}
              <button
                type="button"
                aria-label={`Retirer ${skill.name}`}
                className="rounded-full outline-none hover:text-destructive"
                onClick={() => remove(skill.id)}
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
        </div>
      ) : null}

      <Popover modal open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            variant="outline"
            role="combobox"
            aria-expanded={open}
            disabled={isLoading || isError}
            className="h-10 w-full justify-between rounded-lg font-normal"
          >
            <span className="flex items-center gap-2 text-muted-foreground">
              <Plus className="size-4 shrink-0" />
              {isLoading
                ? "Chargement des compétences…"
                : isError
                  ? "Impossible de charger le référentiel"
                  : available.length === 0
                    ? "Toutes les compétences sont déjà ajoutées"
                    : "Ajouter une compétence"}
            </span>
            <ChevronsUpDown className="size-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          align="start"
          className="z-[80] w-[var(--radix-popover-trigger-width)] p-0"
          onOpenAutoFocus={(event) => event.preventDefault()}
        >
          <Command>
            <CommandInput placeholder={placeholder} />
            <CommandList>
              <CommandEmpty>Aucune compétence trouvée.</CommandEmpty>
              <CommandGroup>
                {available.map((skill) => (
                  <CommandItem
                    key={skill.id}
                    value={skill.name}
                    keywords={[skill.name]}
                    onSelect={() => add(skill.id)}
                    className="cursor-pointer"
                  >
                    <Check
                      className={cn(
                        "mr-2 size-4 opacity-0",
                        value.includes(skill.id) && "opacity-100"
                      )}
                    />
                    <span>{skill.name}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
