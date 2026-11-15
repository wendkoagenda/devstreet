import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
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

export default function ChannelsPage() {
  const { t } = useTranslation();
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
      toast.error(t("forum.name_required"));
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
      toast.success(t("forum.channel_created"));
      setNom("");
      setDescription("");
      setAcces("PUBLIC");
      setCommentairesOuverts(true);
      setShowForm(false);
      navigate(`/forum/chaines/${created.id}`);
    } catch {
      toast.error(t("forum.channel_create_error"));
    }
  };

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4">
      <header className="flex items-center justify-between gap-3 px-1">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground">
            {t("forum.channels_title")}
          </h1>
        </div>
        <Button
          type="button"
          size="icon"
          aria-label={t("forum.create_channel")}
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
            placeholder={t("forum.channel_name_placeholder")}
            maxLength={120}
          />
          <Textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder={t("forum.description_optional")}
            className="min-h-[72px]"
          />
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              variant={acces === "PUBLIC" ? "default" : "outline"}
              onClick={() => setAcces("PUBLIC")}
            >
              {t("forum.access_public")}
            </Button>
            <Button
              type="button"
              size="sm"
              variant={acces === "LIEN" ? "default" : "outline"}
              onClick={() => setAcces("LIEN")}
            >
              {t("forum.access_link")}
            </Button>
            <Button
              type="button"
              size="sm"
              variant={commentairesOuverts ? "default" : "outline"}
              onClick={() => setCommentairesOuverts((open) => !open)}
            >
              {commentairesOuverts
                ? t("forum.comments_open")
                : t("forum.comments_closed")}
            </Button>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setShowForm(false)}
            >
              {t("actions.cancel")}
            </Button>
            <Button type="button" disabled={creating} onClick={handleCreate}>
              {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {t("actions.create")}
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
        searchPlaceholder={t("forum.search_channel")}
        mineTitle={t("forum.my_channels")}
        otherTitle={t("forum.discover")}
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={Boolean(hasNextPage)}
        onLoadMore={() => {
          void fetchNextPage();
        }}
        emptyLabel={
          isError ? t("forum.load_channels_error") : t("forum.empty_channels")
        }
        emptySearchLabel={t("forum.empty_channels_search")}
      />
      {isError ? (
        <div className="flex justify-center">
          <Button type="button" variant="outline" onClick={() => refetch()}>
            {t("forum.retry")}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
