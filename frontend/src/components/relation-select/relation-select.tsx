import { useState } from "react";
import { Check, ChevronsUpDown, X } from "lucide-react";
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

export type RelationSelectProps<T extends { id: number }> = {
  /** Identifiant sélectionné (null / undefined : aucun). */
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  /** Options proposées (la page courante renvoyée par le serveur). */
  items: T[];
  getLabel: (item: T) => string;
  /** Recherche côté serveur : appelée à chaque frappe (à debouncer par l'appelant). */
  onSearchChange?: (search: string) => void;
  isLoading?: boolean;
  /** Élément déjà lié (édition) : affiche son libellé avant que la liste ne le contienne. */
  selectedItem?: T | null;
  placeholder?: string;
  /** Permet de vider le champ (relation facultative). */
  clearable?: boolean;
  disabled?: boolean;
};

/** Sélecteur de relation avec recherche : liste déroulante filtrable alimentée par une requête serveur. */
export function RelationSelect<T extends { id: number }>({
  value,
  onChange,
  items,
  getLabel,
  onSearchChange,
  isLoading = false,
  selectedItem,
  placeholder = "Sélectionner...",
  clearable = false,
  disabled = false,
}: RelationSelectProps<T>) {
  const [open, setOpen] = useState(false);

  const current =
    value == null
      ? null
      : (items.find((item) => item.id === value) ??
        (selectedItem && selectedItem.id === value ? selectedItem : null));
  const currentLabel =
    value == null ? "" : current ? getLabel(current) : `#${value}`;

  return (
    <Popover
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) onSearchChange?.("");
      }}
    >
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className="h-10 w-full justify-between font-normal"
        >
          <span
            className={cn("truncate", value == null && "text-muted-foreground")}
          >
            {value == null ? placeholder : currentLabel}
          </span>
          <span className="flex items-center gap-1">
            {clearable && value != null && !disabled && (
              <span
                role="button"
                aria-label="Effacer"
                className="rounded-sm p-0.5 hover:bg-muted"
                onClick={(event) => {
                  event.stopPropagation();
                  onChange(null);
                }}
              >
                <X className="h-3.5 w-3.5" />
              </span>
            )}
            <ChevronsUpDown className="h-4 w-4 opacity-50" />
          </span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-0 w-[var(--radix-popover-trigger-width)]">
        {/* Le filtrage est fait par le serveur : cmdk ne doit pas refiltrer les résultats */}
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Rechercher..."
            onValueChange={(search) => onSearchChange?.(search)}
          />
          <CommandList>
            <CommandEmpty>
              {isLoading ? "Chargement..." : "Aucun résultat."}
            </CommandEmpty>
            <CommandGroup>
              {items.map((item) => (
                <CommandItem
                  key={item.id}
                  value={String(item.id)}
                  onSelect={() => {
                    onChange(item.id);
                    setOpen(false);
                  }}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      value === item.id ? "opacity-100" : "opacity-0"
                    )}
                  />
                  <span className="truncate">{getLabel(item)}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
