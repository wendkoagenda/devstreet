import { useMemo, useState } from "react";
import { Check, ChevronsUpDown, Loader2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { normalizeSearch } from "./countries";
import { useGetCountryCitiesQuery } from "./geo-api";

/** Nombre de villes affichées à la fois (certains pays en comptent plus de 10 000). */
const MAX_VISIBLE = 50;

export type CitySelectProps = {
  /** Pays sélectionné (code ISO) : la liste des villes en dépend. */
  country: string | null | undefined;
  value: string | null | undefined;
  onChange: (city: string) => void;
  placeholder?: string;
  disabled?: boolean;
  maxLength?: number;
};

/**
 * Ville du pays choisi, avec recherche. Une ville absente de la liste reste saisissable (« Utiliser … »).
 * Sans liste disponible (service indisponible, pays inconnu), le champ redevient une saisie libre.
 */
export function CitySelect({
  country,
  value,
  onChange,
  placeholder = "Choisir une ville",
  disabled = false,
  maxLength = 100,
}: CitySelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const code = (country ?? "").toUpperCase();
  const { data, isFetching, isError } = useGetCountryCitiesQuery(code, { skip: code.length !== 2 });

  const cities = useMemo(() => data?.cities ?? [], [data]);
  const matches = useMemo(() => {
    const query = normalizeSearch(search);
    const filtered = query ? cities.filter((city) => normalizeSearch(city).includes(query)) : cities;
    return filtered.slice(0, MAX_VISIBLE);
  }, [cities, search]);

  const typed = search.trim().slice(0, maxLength);
  const exactMatch = cities.some((city) => normalizeSearch(city) === normalizeSearch(typed));

  // Saisie libre : pas de liste pour ce pays (ou service indisponible)
  if (code.length === 2 && !isFetching && (isError || (data && !data.available))) {
    return (
      <Input
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Saisissez votre ville"
        maxLength={maxLength}
        disabled={disabled}
      />
    );
  }

  const select = (city: string) => {
    onChange(city);
    setOpen(false);
    setSearch("");
  };

  return (
    <Popover
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) setSearch("");
      }}
    >
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled || code.length !== 2}
          className="h-10 w-full justify-between font-normal"
        >
          <span className={cn("truncate", !value && "text-muted-foreground")}>
            {value || (code.length === 2 ? placeholder : "Choisissez d'abord un pays")}
          </span>
          {isFetching ? (
            <Loader2 className="h-4 w-4 shrink-0 animate-spin opacity-50" />
          ) : (
            <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-[var(--radix-popover-trigger-width)] min-w-64 p-0">
        <Command shouldFilter={false}>
          <CommandInput placeholder="Rechercher une ville…" value={search} onValueChange={setSearch} />
          <CommandList>
            <CommandEmpty>{isFetching ? "Chargement des villes…" : "Aucune ville trouvée."}</CommandEmpty>
            {typed && !exactMatch ? (
              <CommandGroup>
                <CommandItem value={`__libre__${typed}`} onSelect={() => select(typed)} className="gap-2">
                  <Plus className="h-4 w-4" aria-hidden />
                  Utiliser « {typed} »
                </CommandItem>
              </CommandGroup>
            ) : null}
            {matches.length > 0 ? (
              <CommandGroup heading={search ? undefined : "Villes"}>
                {matches.map((city) => (
                  <CommandItem key={city} value={city} onSelect={() => select(city)}>
                    <span className="truncate">{city}</span>
                    <Check className={cn("ml-auto h-4 w-4", value === city ? "opacity-100" : "opacity-0")} />
                  </CommandItem>
                ))}
              </CommandGroup>
            ) : null}
            {cities.length > MAX_VISIBLE && !search ? (
              <p className="px-3 py-2 text-xs text-muted-foreground">
                {cities.length} villes : tapez pour affiner la recherche.
              </p>
            ) : null}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
