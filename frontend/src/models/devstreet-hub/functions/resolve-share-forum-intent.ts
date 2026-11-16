import { toast } from "sonner";
import type { ComposerMode } from "@/models/forum/components/feed-composer";
import type { ForumLinkedPublication, ForumPostKind } from "../schema";

/**
 * Ouvre le partage forum après contrôle vitrine Application unique.
 * Retourne le mode à ouvrir, ou null si redirection / blocage.
 */
export async function resolveShareForumIntent(options: {
  kind: ComposerMode;
  projectId: number;
  demoUrl?: string | null;
  listForumPosts: (args: {
    projectId: number;
    kind?: ForumPostKind;
  }) => {
    unwrap: () => Promise<{ results: ForumLinkedPublication[] }>;
  };
  t: (key: string, opts?: Record<string, unknown>) => string;
  navigate: (path: string) => void;
}): Promise<ComposerMode | null> {
  const { kind, projectId, demoUrl, listForumPosts, t, navigate } = options;

  if (kind === "APPLICATION") {
    if (!demoUrl?.trim()) {
      toast.error(t("hub.detail.share_forum.errors.demo_required"));
      return null;
    }
    try {
      const page = await listForumPosts({
        projectId,
        kind: "APPLICATION",
      }).unwrap();
      const existing = page.results ?? [];
      if (existing.length > 0) {
        const pubId = existing[0].id;
        toast.message(t("hub.detail.share_forum.existing_showcase"), {
          action: {
            label: t("hub.detail.share_forum.open_forum"),
            onClick: () => navigate(`/forum/publications/${pubId}`),
          },
        });
        return null;
      }
    } catch {
      toast.error(t("hub.detail.share_forum.errors.list_failed"));
      return null;
    }
  }

  return kind;
}
