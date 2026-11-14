import { profilePath } from "@/helpers/routes/profile-path";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Briefcase,
  FolderKanban,
  Home,
  Radio,
  UserRound,
  Users,
} from "lucide-react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import { useLazySearchMembresQuery } from "@/models/forum/api";
import { ForumAvatar } from "@/models/forum/components/forum-avatar";

type GlobalSearchDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

const QUICK_LINKS = [
  { label: "Fil d'actualité", href: "/", icon: Home },
  { label: "Explorer les projets", href: "/hub/projects", icon: FolderKanban },
  { label: "Communautés", href: "/forum/communautes", icon: Users },
  { label: "Chaînes", href: "/forum/chaines", icon: Radio },
  { label: "Marketplace", href: "/marketplace", icon: Briefcase },
  { label: "Mon profil", href: "/profil/me", icon: UserRound },
] as const;

export function GlobalSearchDialog({
  open,
  onOpenChange,
}: GlobalSearchDialogProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [searchMembres, { data: membres = [], isFetching }] =
    useLazySearchMembresQuery();

  useEffect(() => {
    if (!open) {
      setQuery("");
      return;
    }
    const q = query.trim();
    if (q.length < 2) return;
    const handle = window.setTimeout(() => {
      void searchMembres(q);
    }, 200);
    return () => window.clearTimeout(handle);
  }, [open, query, searchMembres]);

  const filteredLinks = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return QUICK_LINKS;
    return QUICK_LINKS.filter((link) => link.label.toLowerCase().includes(q));
  }, [query]);

  const go = (href: string) => {
    onOpenChange(false);
    navigate(href);
  };

  const goHubSearch = () => {
    const q = query.trim();
    onOpenChange(false);
    navigate(
      q
        ? `/hub/projects?search=${encodeURIComponent(q)}`
        : "/hub/projects"
    );
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        value={query}
        onValueChange={setQuery}
        placeholder="Rechercher projets, technos, développeurs…"
      />
      <CommandList>
        <CommandEmpty>
          {isFetching ? "Recherche…" : "Aucun résultat."}
        </CommandEmpty>

        {query.trim().length >= 2 ? (
          <CommandGroup heading="Hub">
            <CommandItem onSelect={goHubSearch}>
              <FolderKanban className="mr-2 size-4" aria-hidden />
              Projets contenant « {query.trim()} »
            </CommandItem>
          </CommandGroup>
        ) : null}

        {membres.length > 0 ? (
          <CommandGroup heading="Développeurs">
            {membres.slice(0, 6).map((membre) => (
              <CommandItem
                key={membre.id}
                value={`membre-${membre.username}`}
                onSelect={() => go(profilePath(membre.username))}
              >
                <ForumAvatar
                  name={membre.full_name || membre.username}
                  photo={membre.photo}
                  size="sm"
                  tone="soft"
                />
                <span className="ml-2 min-w-0">
                  <span className="block truncate text-sm font-medium">
                    {membre.full_name || membre.username}
                  </span>
                  <span className="block truncate text-xs text-muted-foreground">
                    @{membre.username}
                  </span>
                </span>
              </CommandItem>
            ))}
          </CommandGroup>
        ) : null}

        <CommandSeparator />

        <CommandGroup heading="Raccourcis">
          {filteredLinks.map((link) => {
            const Icon = link.icon;
            return (
              <CommandItem
                key={link.href}
                value={link.label}
                onSelect={() => go(link.href)}
              >
                <Icon className="mr-2 size-4" aria-hidden />
                {link.label}
              </CommandItem>
            );
          })}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
