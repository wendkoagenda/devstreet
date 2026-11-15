import { useMemo, useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { CountryFlag } from "./country-flag";
import { filterCountries, findCountry, type CountryOption } from "./countries";

export type CountrySelectProps = {
  /** Code ISO à 2 lettres ("" : aucun). */
  value: string | null | undefined;
  onChange: (code: string) => void;
  placeholder?: string;
  disabled?: boolean;
  /** Affiche l'indicatif téléphonique à côté du nom (sélecteur d'indicatif). */
  showDialCode?: boolean;
  /** Bouton compact (drapeau + indicatif seulement), pour le champ téléphone. */
  compact?: boolean;
  className?: string;
  "aria-label"?: string;
};

/** Sélecteur de pays : drapeau, nom en français, recherche sans accents (nom, code ou indicatif). */
export function CountrySelect({
  value,
  onChange,
  placeholder = "Choisir un pays",
  disabled = false,
  showDialCode = false,
  compact = false,
  className,
  "aria-label": ariaLabel,
}: CountrySelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const current = findCountry(value);
  const results = useMemo(() => filterCountries(search), [search]);
  const suggested = search ? [] : results.filter((item) => item.suggested);
  const others = search ? results : results.filter((item) => !item.suggested);

  const select = (item: CountryOption) => {
    onChange(item.code);
    setOpen(false);
    setSearch("");
  };

  const renderItem = (item: CountryOption) => (
    <CommandItem key={item.code} value={item.code} onSelect={() => select(item)} className="gap-2">
      <CountryFlag code={item.code} />
      <span className="truncate">{item.name}</span>
      {showDialCode ? <span className="ml-auto pl-2 text-xs text-muted-foreground">+{item.dialCode}</span> : null}
      <Check className={cn("h-4 w-4 shrink-0", showDialCode ? "ml-1" : "ml-auto", current?.code === item.code ? "opacity-100" : "opacity-0")} />
    </CommandItem>
  );

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
          aria-label={ariaLabel ?? (current ? `Pays : ${current.name}` : placeholder)}
          disabled={disabled}
          className={cn("h-10 justify-between gap-2 font-normal", compact ? "w-auto px-2.5" : "w-full", className)}
        >
          {current ? (
            <span className="flex min-w-0 items-center gap-2">
              <CountryFlag code={current.code} />
              {compact ? (
                <span className="text-sm">+{current.dialCode}</span>
              ) : (
                <span className="truncate">{current.name}</span>
              )}
            </span>
          ) : (
            <span className="truncate text-muted-foreground">{compact ? "Pays" : placeholder}</span>
          )}
          <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        className={cn("p-0", compact ? "w-72" : "w-[var(--radix-popover-trigger-width)] min-w-64")}
      >
        {/* Filtrage maison (accents, indicatif) : cmdk ne refiltre pas */}
        <Command shouldFilter={false}>
          <CommandInput placeholder="Rechercher un pays ou un indicatif…" value={search} onValueChange={setSearch} />
          <CommandList>
            <CommandEmpty>Aucun pays trouvé.</CommandEmpty>
            {suggested.length > 0 ? <CommandGroup heading="Suggérés">{suggested.map(renderItem)}</CommandGroup> : null}
            {others.length > 0 ? (
              <CommandGroup heading={search ? undefined : "Tous les pays"}>{others.map(renderItem)}</CommandGroup>
            ) : null}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
