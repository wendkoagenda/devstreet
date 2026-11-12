import {
  BookMarked,
  Check,
  ChevronRight,
  Copy,
  File,
  Folder,
  GitBranch,
  GitCommitHorizontal,
  HardDrive,
  Tag,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { SafeMarkdown } from "../functions/safe-markdown";
import { useProjectCode } from "../hooks/use-project-code";
import { CodeFileViewer } from "./code-file-viewer";

interface CodeBrowserProps {
  projectId: number;
  projectTitle: string;
  isOwner: boolean;
  namespaceHint?: string | null;
  repoNameHint?: string | null;
}

async function copyText(value: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    return false;
  }
}

function formatRelative(iso: string | null | undefined, fallback: string): string {
  if (!iso) return fallback;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return fallback;
  const diff = Date.now() - date.getTime();
  const minutes = Math.round(diff / 60000);
  if (minutes < 1) return fallback;
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 48) return `${hours} h`;
  const days = Math.round(hours / 24);
  return `${days} j`;
}

export function CodeBrowser({
  projectId,
  projectTitle,
  isOwner,
  namespaceHint,
  repoNameHint,
}: CodeBrowserProps) {
  const { t } = useTranslation();
  const code = useProjectCode(projectId, { enabled: true, isOwner });
  const [copiedClone, setCopiedClone] = useState(false);

  const repoLabel = useMemo(() => {
    const ns = namespaceHint || "…";
    const name = repoNameHint || "…";
    return `${ns} / ${name}`;
  }, [namespaceHint, repoNameHint]);

  const cloneUrl = code.summary?.clone_url ?? null;

  const handleCopyClone = async () => {
    if (!cloneUrl) return;
    const ok = await copyText(cloneUrl);
    if (ok) {
      setCopiedClone(true);
      window.setTimeout(() => setCopiedClone(false), 1600);
    }
  };

  if (code.isLoading && !code.summary) {
    return (
      <p className="rounded-lg border border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </p>
    );
  }

  if (code.isError && !code.summary) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-10 text-center">
        <p className="text-sm text-destructive">
          {code.errorStatus === 503
            ? t("hub.detail.code.forge_unavailable")
            : code.errorStatus === 403
              ? t("hub.detail.errors.forbidden")
              : t("hub.detail.code.load_error")}
        </p>
        <Button type="button" variant="outline" className="h-8 text-xs" onClick={code.retry}>
          {t("hub.common.retry")}
        </Button>
      </div>
    );
  }

  if (code.isEmpty) {
    return (
      <div className="flex flex-col gap-4 rounded-lg border border-dashed border-border bg-card p-6">
        <h3 className="text-sm font-bold text-foreground">{t("hub.detail.code.empty_title")}</h3>
        <p className="text-sm text-muted-foreground">{t("hub.detail.code.empty_text")}</p>
        {cloneUrl ? (
          <p className="break-all rounded-md border border-border bg-muted/40 px-3 py-2 font-mono text-xs">
            {cloneUrl}
          </p>
        ) : null}
        {code.canInitialize ? (
          <Button
            type="button"
            className="h-9 w-fit text-xs font-semibold"
            disabled={code.isInitializing}
            onClick={() => {
              void code.initReadme();
            }}
          >
            {code.isInitializing
              ? t("hub.detail.code.initializing")
              : t("hub.detail.code.init_readme")}
          </Button>
        ) : null}
      </div>
    );
  }

  if (code.mode === "blob") {
    if (code.isLoading || (code.isFetching && !code.blob && !code.isError)) {
      return (
        <p className="rounded-lg border border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground">
          {t("common.loading")}
        </p>
      );
    }
    if (code.blob) {
      return (
        <CodeFileViewer
          blob={code.blob}
          onBack={() => {
            const parent = code.path.includes("/")
              ? code.path.split("/").slice(0, -1).join("/")
              : "";
            code.openPath(parent, "tree");
          }}
        />
      );
    }
    return (
      <div className="flex flex-col items-center gap-3 rounded-lg border border-border bg-card px-4 py-10 text-center">
        <p className="text-sm text-muted-foreground">{t("hub.detail.code.file_not_found")}</p>
        <Button type="button" variant="outline" className="h-8 text-xs" onClick={code.goRoot}>
          {t("hub.detail.code.back_tree")}
        </Button>
      </div>
    );
  }

  const entries = code.tree?.entries ?? [];
  const commit = code.tree?.latest_commit;
  const stats = code.summary?.stats;

  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-start">
      <div className="min-w-0 flex-1">
        <div className="mb-3 flex flex-wrap items-center gap-2 text-sm">
          <BookMarked aria-hidden className="size-4 text-muted-foreground" />
          <span className="font-semibold text-foreground">{repoLabel}</span>
        </div>

        <div className="mb-3 flex flex-wrap items-center gap-4 rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <GitCommitHorizontal aria-hidden className="size-3.5" />
            {stats?.commits != null
              ? t("hub.detail.code.stat_commits", { count: stats.commits })
              : t("hub.detail.code.stat_commits_unknown")}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <GitBranch aria-hidden className="size-3.5" />
            {stats?.branches != null
              ? t("hub.detail.code.stat_branches", { count: stats.branches })
              : t("hub.detail.code.stat_na")}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Tag aria-hidden className="size-3.5" />
            {stats?.tags != null
              ? t("hub.detail.code.stat_tags", { count: stats.tags })
              : t("hub.detail.code.stat_na")}
          </span>
        </div>

        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            <Select value={code.ref} onValueChange={code.setBranch}>
              <SelectTrigger className="h-8 w-[min(100%,14rem)] rounded-md bg-card text-xs">
                <GitBranch aria-hidden className="mr-1.5 size-3.5" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {(code.branches.length
                  ? code.branches.map((b) => b.name)
                  : [code.ref]
                ).map((name) => (
                  <SelectItem key={name} value={name} className="text-xs">
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <nav aria-label={t("hub.detail.code.breadcrumb")} className="flex flex-wrap items-center gap-0.5 text-xs">
              {code.breadcrumbs.map((crumb, index) => {
                const isLast = index === code.breadcrumbs.length - 1;
                return (
                  <span key={crumb.path || "root"} className="inline-flex items-center">
                    {index > 0 ? (
                      <ChevronRight aria-hidden className="mx-0.5 size-3 text-muted-foreground" />
                    ) : null}
                    {isLast ? (
                      <span className="font-semibold text-foreground">
                        {crumb.label || projectTitle}
                      </span>
                    ) : (
                      <button
                        type="button"
                        className="rounded px-1 text-brand hover:underline"
                        onClick={() => code.openPath(crumb.path, "tree")}
                      >
                        {crumb.label || projectTitle}
                      </button>
                    )}
                  </span>
                );
              })}
            </nav>
          </div>

          {cloneUrl ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button className="h-8 gap-1.5 rounded-md text-xs font-semibold">
                  {t("hub.detail.code.clone_menu")}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80 p-3">
                <p className="mb-2 text-[11px] font-semibold text-muted-foreground">
                  {t("hub.detail.code.clone_https")}
                </p>
                <div className="flex items-center gap-2">
                  <code className="min-w-0 flex-1 truncate rounded border border-border bg-muted/50 px-2 py-1.5 text-[11px]">
                    {cloneUrl}
                  </code>
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    className="h-8 shrink-0 gap-1 text-xs"
                    onClick={() => void handleCopyClone()}
                  >
                    {copiedClone ? (
                      <Check aria-hidden className="size-3.5" />
                    ) : (
                      <Copy aria-hidden className="size-3.5" />
                    )}
                  </Button>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : null}
        </div>

        <div className="overflow-hidden rounded-lg border border-border bg-card">
          {commit ? (
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-muted/30 px-3 py-2 text-xs">
              <div className="min-w-0 flex flex-wrap items-center gap-2">
                <span className="font-semibold text-foreground">
                  {commit.author_name || t("hub.detail.code.unknown_author")}
                </span>
                <span className="font-mono text-muted-foreground">{commit.short_sha}</span>
                <span className="truncate text-muted-foreground">{commit.message}</span>
              </div>
              <span className="text-muted-foreground">
                {formatRelative(commit.authored_at, t("hub.detail.code.just_now"))}
              </span>
            </div>
          ) : null}

          {code.isError ? (
            <div className="flex flex-col items-center gap-2 px-4 py-8 text-center">
              <p className="text-sm text-muted-foreground">
                {code.errorStatus === 404
                  ? t("hub.detail.code.path_not_found")
                  : t("hub.detail.code.load_error")}
              </p>
              <Button type="button" variant="outline" className="h-8 text-xs" onClick={code.retry}>
                {t("hub.common.retry")}
              </Button>
            </div>
          ) : entries.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-muted-foreground">
              {t("hub.detail.code.folder_empty")}
            </p>
          ) : (
            <ul className="divide-y divide-border">
              {code.path ? (
                <li>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs hover:bg-muted/40"
                    onClick={() => {
                      const parent = code.path.includes("/")
                        ? code.path.split("/").slice(0, -1).join("/")
                        : "";
                      code.openPath(parent, "tree");
                    }}
                  >
                    <Folder aria-hidden className="size-4 text-muted-foreground" />
                    <span className="font-medium text-foreground">..</span>
                  </button>
                </li>
              ) : null}
              {entries.map((entry) => (
                <li key={entry.path}>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs hover:bg-muted/40"
                    onClick={() =>
                      code.openPath(
                        entry.path,
                        entry.type === "dir" ? "tree" : "blob"
                      )
                    }
                  >
                    {entry.type === "dir" ? (
                      <Folder aria-hidden className="size-4 shrink-0 text-brand" />
                    ) : (
                      <File aria-hidden className="size-4 shrink-0 text-muted-foreground" />
                    )}
                    <span
                      className={cn(
                        "min-w-0 flex-1 truncate font-medium",
                        entry.type === "dir" ? "text-foreground" : "text-foreground"
                      )}
                    >
                      {entry.name}
                    </span>
                    {commit ? (
                      <span className="hidden max-w-[40%] truncate text-muted-foreground md:inline">
                        {commit.message}
                      </span>
                    ) : null}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {code.tree?.readme ? (
          <section className="mt-4 overflow-hidden rounded-lg border border-border bg-card">
            <div className="border-b border-border bg-muted/30 px-3 py-2 text-xs font-semibold text-foreground">
              {code.tree.readme.name}
            </div>
            <div className="p-4">
              <SafeMarkdown content={code.tree.readme.content} />
              {code.tree.readme.truncated ? (
                <p className="mt-2 text-xs text-muted-foreground">
                  {t("hub.detail.code.readme_truncated")}
                </p>
              ) : null}
            </div>
          </section>
        ) : null}
      </div>

      <aside className="w-full shrink-0 lg:w-64">
        <div className="flex flex-col gap-4 rounded-lg border border-border bg-card p-4 text-xs">
          <div>
            <h3 className="mb-1.5 font-semibold text-foreground">
              {t("hub.detail.code.sidebar_description")}
            </h3>
            <p className="leading-relaxed text-muted-foreground">
              {code.summary?.description || t("hub.detail.code.no_description")}
            </p>
          </div>
          <ul className="flex flex-col gap-1.5 text-muted-foreground">
            {code.summary?.size_kib != null ? (
              <li className="inline-flex items-center gap-1.5">
                <HardDrive aria-hidden className="size-3.5" />
                {t("hub.detail.code.size", { size: code.summary.size_kib })}
              </li>
            ) : null}
          </ul>
          {(code.summary?.languages?.length ?? 0) > 0 ? (
            <div>
              <h3 className="mb-2 font-semibold text-foreground">
                {t("hub.detail.code.languages")}
              </h3>
              <div className="mb-2 flex h-2 overflow-hidden rounded-full bg-muted">
                {code.summary!.languages.map((lang, index) => (
                  <span
                    key={lang.name}
                    className={cn(
                      "h-full",
                      index % 3 === 0 && "bg-brand",
                      index % 3 === 1 && "bg-info",
                      index % 3 === 2 && "bg-warning"
                    )}
                    style={{ width: `${lang.percent}%` }}
                    title={`${lang.name} ${lang.percent}%`}
                  />
                ))}
              </div>
              <ul className="flex flex-col gap-1">
                {code.summary!.languages.map((lang) => (
                  <li key={lang.name} className="flex justify-between gap-2">
                    <span className="text-foreground">{lang.name}</span>
                    <span className="text-muted-foreground">{lang.percent}%</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </aside>
    </div>
  );
}
