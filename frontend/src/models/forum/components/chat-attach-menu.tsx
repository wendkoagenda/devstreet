import { useRef, useState } from "react";
import {
  FileUp,
  FolderKanban,
  ImagePlus,
  Loader2,
  Paperclip,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthSlice } from "@/models/auth/slice";
import { useGetProjectsQuery } from "@/models/devstreet-hub/api";
import { useUploadForumMediaMutation } from "../api";
import {
  encodeFileMessage,
  encodeImageMessage,
  encodeProjectMessage,
} from "../lib/rich-message";

type ChatAttachMenuProps = {
  disabled?: boolean;
  onSendEncoded: (texte: string) => Promise<void>;
};

const IMAGE_ACCEPT = "image/jpeg,image/png,image/gif,image/webp";
const FILE_ACCEPT =
  ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.md,.csv,.zip,.rar,.7z,.json";

/**
 * Menu d'attache pour le chat : image, fichier, ou partage d'un projet Hub.
 */
export function ChatAttachMenu({
  disabled,
  onSendEncoded,
}: ChatAttachMenuProps) {
  const user = useAuthSlice((state) => state.user);
  const imageInputRef = useRef<HTMLInputElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [uploadMedia, { isLoading: uploading }] = useUploadForumMediaMutation();
  const [busy, setBusy] = useState(false);

  const projects = useGetProjectsQuery(
    { owner: user?.id, page_size: 30 },
    { skip: !user?.id || !menuOpen }
  );

  const sendFile = async (file: File, kind: "IMAGE" | "FILE") => {
    if (disabled || busy || uploading) return;
    setBusy(true);
    try {
      const uploaded = await uploadMedia({ file, kind }).unwrap();
      const texte =
        kind === "IMAGE"
          ? encodeImageMessage(uploaded.url, file.name)
          : encodeFileMessage(uploaded.url, file.name);
      await onSendEncoded(texte);
      setMenuOpen(false);
    } catch {
      toast.error(
        kind === "IMAGE"
          ? "Impossible d'envoyer l'image"
          : "Impossible d'envoyer le fichier"
      );
    } finally {
      setBusy(false);
    }
  };

  const sendProject = async (id: number, title: string) => {
    if (disabled || busy) return;
    setBusy(true);
    try {
      await onSendEncoded(encodeProjectMessage(id, title));
      setMenuOpen(false);
    } catch {
      toast.error("Impossible de partager le projet");
    } finally {
      setBusy(false);
    }
  };

  const working = Boolean(disabled || busy || uploading);

  return (
    <>
      <input
        ref={imageInputRef}
        type="file"
        accept={IMAGE_ACCEPT}
        className="sr-only"
        tabIndex={-1}
        onChange={(event) => {
          const file = event.target.files?.[0];
          event.target.value = "";
          if (file) void sendFile(file, "IMAGE");
        }}
      />
      <input
        ref={fileInputRef}
        type="file"
        accept={FILE_ACCEPT}
        className="sr-only"
        tabIndex={-1}
        onChange={(event) => {
          const file = event.target.files?.[0];
          event.target.value = "";
          if (file) void sendFile(file, "FILE");
        }}
      />

      <DropdownMenu open={menuOpen} onOpenChange={setMenuOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="h-10 w-10 shrink-0"
            disabled={working}
            aria-label="Joindre"
          >
            {working ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Paperclip className="size-4" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-52">
          <DropdownMenuLabel>Joindre</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            disabled={working}
            onSelect={() => imageInputRef.current?.click()}
          >
            <ImagePlus className="size-4" />
            Image
          </DropdownMenuItem>
          <DropdownMenuItem
            disabled={working}
            onSelect={() => fileInputRef.current?.click()}
          >
            <FileUp className="size-4" />
            Fichier
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuSub>
            <DropdownMenuSubTrigger disabled={working}>
              <FolderKanban className="size-4" />
              Projet Hub
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent className="max-h-64 w-64 overflow-y-auto">
              {projects.isLoading ? (
                <DropdownMenuItem disabled>
                  <Loader2 className="size-3.5 animate-spin" />
                  Chargement…
                </DropdownMenuItem>
              ) : null}
              {projects.isError ? (
                <DropdownMenuItem disabled className="text-destructive">
                  Impossible de charger
                </DropdownMenuItem>
              ) : null}
              {!projects.isLoading &&
              !projects.isError &&
              (projects.data?.results.length ?? 0) === 0 ? (
                <DropdownMenuItem disabled>
                  Aucun projet
                </DropdownMenuItem>
              ) : null}
              {(projects.data?.results ?? []).map((project) => (
                <DropdownMenuItem
                  key={project.id}
                  disabled={working}
                  onSelect={() =>
                    void sendProject(project.id, project.title)
                  }
                >
                  <FolderKanban className="size-3.5 shrink-0" />
                  <span className="truncate">{project.title}</span>
                </DropdownMenuItem>
              ))}
            </DropdownMenuSubContent>
          </DropdownMenuSub>
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  );
}
