import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import {
  useCreateEspaceMutation,
  useGetEspacesInfiniteQuery,
} from "../api";
import { EspaceDirectory } from "../components/espace-directory";
import { useDebouncedValue } from "@/hooks/use-debounced-value";

export default function CommunitiesPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
  const {
    data,
    isLoading,
    isError,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    refetch,
  } = useGetEspacesInfiniteQuery({
    type: "COMMUNAUTE",
    page_size: PAGE_SIZE,
    ...(debouncedSearch.trim() ? { search: debouncedSearch.trim() } : {}),
  });
  const [createEspace, { isLoading: creating }] = useCreateEspaceMutation();
  const [showForm, setShowForm] = useState(false);
  const [nom, setNom] = useState("");
  const [description, setDescription] = useState("");
  const [acces, setAcces] = useState<"PUBLIC" | "LIEN">("PUBLIC");

  const espaces = useMemo(
    () => data?.pages.flatMap((page) => page.results) ?? [],
    [data?.pages]
  );

  const handleCreate = async () => {
    const trimmed = nom.trim();
    if (!trimmed) {
      toast.error("Le nom est obligatoire");
      return;
    }
    try {
      const created = await createEspace({
        nom: trimmed,
        description: description.trim(),
        type: "COMMUNAUTE",
        membres_peuvent_publier: true,
        commentaires_ouverts: true,
        acces,
      }).unwrap();
      toast.success("Communauté créée");
      setNom("");
      setDescription("");
      setShowForm(false);
      navigate(`/forum/communautes/${created.id}`);
    } catch {
      toast.error("Impossible de créer la communauté");
    }
  };

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4">
      <header className="flex items-center justify-between gap-3 px-1">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground">
            Communautés
          </h1>
        </div>
        <Button
          type="button"
          size="icon"
          aria-label="Créer une communauté"
          onClick={() => setShowForm((open) => !open)}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </header>

      {showForm ? (
        <section className="space-y-3 rounded-2xl border border-border bg-card p-4">
          <Input
            value={nom}
            onChange={(event) => setNom(event.target.value)}
            placeholder="Nom de la communauté"
            maxLength={120}
          />
          <Textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Description (facultatif)"
            className="min-h-[72px]"
          />
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              variant={acces === "PUBLIC" ? "default" : "outline"}
              onClick={() => setAcces("PUBLIC")}
            >
              Public
            </Button>
            <Button
              type="button"
              size="sm"
              variant={acces === "LIEN" ? "default" : "outline"}
              onClick={() => setAcces("LIEN")}
            >
              Accès par lien
            </Button>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setShowForm(false)}
            >
              Annuler
            </Button>
            <Button type="button" disabled={creating} onClick={handleCreate}>
              {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Créer
            </Button>
          </div>
        </section>
      ) : null}

      <EspaceDirectory
        espaces={isError ? [] : espaces}
        hrefFor={(espace) =>
          espace.mon_role
            ? `/messages?groupe=${espace.id}`
            : `/forum/communautes/${espace.id}`
        }
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Rechercher une communauté…"
        mineTitle="Mes communautés"
        otherTitle="À découvrir"
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={Boolean(hasNextPage)}
        onLoadMore={() => {
          void fetchNextPage();
        }}
        emptyLabel={
          isError
            ? "Impossible de charger les communautés."
            : "Aucune communauté pour l’instant."
        }
        emptySearchLabel="Aucune communauté ne correspond à ta recherche."
      />
      {isError ? (
        <div className="flex justify-center">
          <Button type="button" variant="outline" onClick={() => refetch()}>
            Réessayer
          </Button>
        </div>
      ) : null}
    </div>
  );
}
