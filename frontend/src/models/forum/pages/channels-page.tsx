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
import {
  EspaceDirectory,
  useDebouncedValue,
} from "../components/espace-directory";

export default function ChannelsPage() {
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
    type: "CHAINE",
    page_size: PAGE_SIZE,
    ...(debouncedSearch.trim() ? { search: debouncedSearch.trim() } : {}),
  });
  const [createEspace, { isLoading: creating }] = useCreateEspaceMutation();
  const [showForm, setShowForm] = useState(false);
  const [nom, setNom] = useState("");
  const [description, setDescription] = useState("");
  const [acces, setAcces] = useState<"PUBLIC" | "LIEN">("PUBLIC");
  const [commentairesOuverts, setCommentairesOuverts] = useState(true);

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
        type: "CHAINE",
        acces,
        membres_peuvent_publier: false,
        commentaires_ouverts: commentairesOuverts,
      }).unwrap();
      toast.success("Chaîne créée");
      setNom("");
      setDescription("");
      setAcces("PUBLIC");
      setCommentairesOuverts(true);
      setShowForm(false);
      navigate(`/forum/chaines/${created.id}`);
    } catch {
      toast.error("Impossible de créer la chaîne");
    }
  };

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4">
      <header className="flex items-center justify-between gap-3 px-1">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground">
            Chaînes
          </h1>
        </div>
        <Button
          type="button"
          size="icon"
          aria-label="Créer une chaîne"
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
            placeholder="Nom de la chaîne"
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
            <Button
              type="button"
              size="sm"
              variant={commentairesOuverts ? "default" : "outline"}
              onClick={() => setCommentairesOuverts((open) => !open)}
            >
              Commentaires : {commentairesOuverts ? "ouverts" : "fermés"}
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
            : `/forum/chaines/${espace.id}`
        }
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Rechercher une chaîne…"
        mineTitle="Mes chaînes"
        otherTitle="À découvrir"
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={Boolean(hasNextPage)}
        onLoadMore={() => {
          void fetchNextPage();
        }}
        emptyLabel={
          isError
            ? "Impossible de charger les chaînes."
            : "Aucune chaîne pour l’instant."
        }
        emptySearchLabel="Aucune chaîne ne correspond à ta recherche."
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
