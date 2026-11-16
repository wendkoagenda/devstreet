import {
  BookMarked,
  Check,
  ChevronRight,
  Code2,
  Copy,
  Download,
  FileCode2,
  Folder,
  GitBranch,
  GitCommitHorizontal,
  HardDrive,
  Tag,
  Terminal,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { API_V1_URL } from "@/helpers/api/csrf";
import { toQueryString } from "@/helpers/api/pagination";
import { languageColor } from "../functions/language-colors";
import { SafeMarkdown } from "../functions/safe-markdown";
import { useProjectCode } from "../hooks/use-project-code";
import { CodeFileViewer } from "./code-file-viewer";
import { CodeBrowserSkeleton, CodeRowsSkeleton } from "./code-browser-skeleton";
import { copyText } from "@/helpers/clipboard";

interface CodeBrowserProps {
  projectId: number;
  projectTitle: string;
  isOwner: boolean;
  namespaceHint?: string | null;
  repoNameHint?: string | null;
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

function fileIconColor(name: string): string {
  const lower = name.toLowerCase();
  if (lower.endsWith(".html") || lower.endsWith(".htm")) return "#e34c26";
  if (lower.endsWith(".css") || lower.endsWith(".scss")) return "#563d7c";
  if (lower.endsWith(".js") || lower.endsWith(".jsx")) return "#f1e05a";
  if (lower.endsWith(".ts") || lower.endsWith(".tsx")) return "#3178c6";
  if (lower.endsWith(".py")) return "#3572A5";
  if (lower.endsWith(".md")) return "#083fa1";
  return "hsl(var(--muted-foreground))";
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
  const [downloading, setDownloading] = useState<"zip" | "tar.gz" | null>(null);

  const repoLabel = useMemo(() => {
    const ns = namespaceHint || "…";
    const name = repoNameHint || "…";
    return { ns, name };
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

  const handleDownloadArchive = async (format: "zip" | "tar.gz") => {
    setDownloading(format);
    try {
      const query = toQueryString({
        ref: code.ref,
        archive_format: format,
      } as Record<string, string>);
      const response = await fetch(
        `${API_V1_URL}/projects/${projectId}/code/archive${query}`,
        { credentials: "include" }
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/i);
      const filename =
        match?.[1] ||
        `${repoNameHint || "project"}-${code.ref.replace(/[^\w.-]+/g, "-")}.${format}`;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error(t("hub.detail.code.download_error"));
    } finally {
      setDownloading(null);
    }
  };

  if (code.isLoading && !code.summary && !code.tree && !code.blob && !code.isError) {
    return <CodeBrowserSkeleton />;
  }

  if (code.isError && !code.summary && !code.tree && !code.blob) {
    return (
      <div className="flex flex-col items-center gap-3 border border-destructive/30 bg-destructive/5 px-4 py-10 text-center">
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
    const branch = code.summary?.default_branch || "main";
    const pushCommands = cloneUrl
      ? [
          "git init",
          "git add .",
          'git commit -m "Premier commit"',
          `git branch -M ${branch}`,
          `git remote add origin ${cloneUrl}`,
          `git push -u origin ${branch}`,
        ].join("\n")
      : null;

    return (
      <div className="flex flex-col gap-4 border border-dashed border-border bg-card p-6">
        <div>
          <h3 className="text-sm font-bold text-foreground">
            {t("hub.detail.code.empty_title")}
          </h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {t("hub.detail.code.empty_push_hint")}
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            <Link
              to="/hub/git-setup"
              className="text-brand underline-offset-2 hover:underline"
            >
              {t("hub.create.repo.git_setup_title_short")}
            </Link>
          </p>
        </div>
        {pushCommands ? (
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-foreground">
                {t("hub.detail.code.first_push_commands")}
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs text-brand"
                onClick={async () => {
                  const ok = await copyText(pushCommands);
                  if (ok) {
                    setCopiedClone(true);
                    window.setTimeout(() => setCopiedClone(false), 1600);
                  }
                }}
              >
                {copiedClone ? t("hub.detail.code.copied") : t("hub.detail.code.copy")}
              </Button>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-primary px-3 py-3 font-sans text-[11px] leading-relaxed text-primary-foreground">
              {pushCommands}
            </pre>
          </div>
        ) : null}
        {code.canInitialize ? (
          <Button
            type="button"
            variant="outline"
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
      return <CodeBrowserSkeleton />;
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
      <div className="flex flex-col items-center gap-3 border border-border bg-card px-4 py-10 text-center">
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
  const languages = code.summary?.languages ?? [];

  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:gap-5">
      <div className="min-w-0 flex-1 space-y-3">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <BookMarked aria-hidden className="size-4 text-muted-foreground" />
          <span className="text-muted-foreground">@{repoLabel.ns}</span>
          <span className="text-muted-foreground">/</span>
          <span className="font-semibold text-foreground">{repoLabel.name}</span>
        </div>

        {code.metadataError ? <p role="status" className="rounded-lg border border-border bg-muted/40 p-3 text-xs text-muted-foreground">{t("hub.detail.code.metadata_unavailable")}</p> : null}
        <div className="grid grid-cols-3 overflow-hidden border border-border bg-muted/30 text-xs">
          <div className="flex items-center justify-center gap-1.5 border-r border-border px-2 py-2 text-muted-foreground">
            <GitCommitHorizontal aria-hidden className="size-3.5 shrink-0" />
            <span>
              {stats?.commits != null
                ? t("hub.detail.code.stat_commits", { count: stats.commits })
                : t("hub.detail.code.stat_commits_unknown")}
            </span>
          </div>
          <div className="flex items-center justify-center gap-1.5 border-r border-border px-2 py-2 text-muted-foreground">
            <GitBranch aria-hidden className="size-3.5 shrink-0" />
            <span>
              {stats?.branches != null
                ? t("hub.detail.code.stat_branches", { count: stats.branches })
                : t("hub.detail.code.stat_na")}
            </span>
          </div>
          <div className="flex items-center justify-center gap-1.5 px-2 py-2 text-muted-foreground">
            <Tag aria-hidden className="size-3.5 shrink-0" />
            <span>
              {stats?.tags != null
                ? t("hub.detail.code.stat_tags", { count: stats.tags })
                : t("hub.detail.code.stat_na")}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            <Select value={code.ref} onValueChange={code.setBranch}>
              <SelectTrigger className="h-8 w-[min(100%,12rem)] rounded-md border-border bg-card text-xs shadow-none">
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

            <nav
              aria-label={t("hub.detail.code.breadcrumb")}
              className="flex flex-wrap items-center gap-0.5 text-xs"
            >
              {code.breadcrumbs.map((crumb, index) => {
                const isLast = index === code.breadcrumbs.length - 1;
                return (
                  <span key={crumb.path || "root"} className="inline-flex items-center">
                    {index > 0 ? (
                      <ChevronRight
                        aria-hidden
                        className="mx-0.5 size-3 text-muted-foreground"
                      />
                    ) : null}
                    {isLast ? (
                      <span className="font-semibold text-foreground">
                        {crumb.label || projectTitle}
                      </span>
                    ) : (
                      <button
                        type="button"
                        className="rounded px-1 text-info hover:underline"
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

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="h-8 gap-1.5 rounded-md bg-info px-3 text-xs font-semibold text-info-foreground hover:bg-info/90">
                <Code2 aria-hidden className="size-3.5" />
                {t("hub.detail.code.clone_menu")}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[22rem] space-y-3 p-3">
              {cloneUrl ? (
                <div>
                  <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-foreground">
                    <Terminal aria-hidden className="size-3.5" />
                    {t("hub.detail.code.clone_https")}
                  </div>
                  <div className="flex items-center gap-2">
                    <code className="min-w-0 flex-1 truncate rounded-md border border-border bg-muted/50 px-2 py-1.5 text-[11px]">
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
                </div>
              ) : null}
              <div className="border-t border-border pt-3">
                <p className="mb-2 text-[11px] font-semibold text-muted-foreground">
                  {t("hub.detail.code.download_section")}
                </p>
                <div className="flex flex-col gap-1.5">
                  <Button
                    type="button"
                    variant="outline"
                    className="h-8 justify-start gap-2 text-xs"
                    disabled={downloading !== null}
                    onClick={() => void handleDownloadArchive("zip")}
                  >
                    <Download aria-hidden className="size-3.5" />
                    {downloading === "zip"
                      ? t("hub.detail.code.downloading")
                      : t("hub.detail.code.download_zip")}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    className="h-8 justify-start gap-2 text-xs"
                    disabled={downloading !== null}
                    onClick={() => void handleDownloadArchive("tar.gz")}
                  >
                    <Download aria-hidden className="size-3.5" />
                    {downloading === "tar.gz"
                      ? t("hub.detail.code.downloading")
                      : t("hub.detail.code.download_targz")}
                  </Button>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="overflow-hidden border border-border bg-card">
          {commit ? (
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-muted/40 px-3 py-2 text-xs">
              <div className="flex min-w-0 flex-wrap items-center gap-2">
                <span
                  aria-hidden
                  className="flex size-5 shrink-0 items-center justify-center rounded-sm bg-success/20 text-[10px] font-bold text-success"
                >
                  {(commit.author_name || "?").slice(0, 1).toUpperCase()}
                </span>
                <span className="font-semibold text-foreground">
                  {commit.author_name || t("hub.detail.code.unknown_author")}
                </span>
                <span className="font-mono text-muted-foreground">{commit.short_sha}</span>
                <span className="truncate text-muted-foreground">{commit.message}</span>
              </div>
              <span className="shrink-0 text-muted-foreground">
                {formatRelative(commit.authored_at, t("hub.detail.code.just_now"))}
              </span>
            </div>
          ) : null}

          {code.isLoading ? (
            <div role="status" aria-busy="true"><span className="sr-only">{t("common.loading")}</span><CodeRowsSkeleton /></div>
          ) : code.isError ? (
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
                    className="grid w-full grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)_auto] items-center gap-2 px-3 py-2 text-left text-xs hover:bg-muted/40"
                    onClick={() => {
                      const parent = code.path.includes("/")
                        ? code.path.split("/").slice(0, -1).join("/")
                        : "";
                      code.openPath(parent, "tree");
                    }}
                  >
                    <span className="inline-flex items-center gap-2 font-medium text-foreground">
                      <Folder aria-hidden className="size-4 text-muted-foreground" />
                      ..
                    </span>
                    <span />
                    <span />
                  </button>
                </li>
              ) : null}
              {entries.map((entry) => (
                <li key={entry.path}>
                  <button
                    type="button"
                    className="grid w-full grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)_auto] items-center gap-2 px-3 py-2 text-left text-xs hover:bg-muted/40"
                    onClick={() =>
                      code.openPath(
                        entry.path,
                        entry.type === "dir" ? "tree" : "blob"
                      )
                    }
                  >
                    <span className="inline-flex min-w-0 items-center gap-2 font-medium text-foreground">
                      {entry.type === "dir" ? (
                        <Folder aria-hidden className="size-4 shrink-0 text-info" />
                      ) : (
                        <FileCode2
                          aria-hidden
                          className="size-4 shrink-0"
                          style={{ color: fileIconColor(entry.name) }}
                        />
                      )}
                      <span className="truncate">{entry.name}</span>
                    </span>
                    <span className="hidden truncate text-muted-foreground md:inline">
                      {commit?.message || ""}
                    </span>
                    <span className="hidden shrink-0 text-muted-foreground sm:inline">
                      {formatRelative(
                        commit?.authored_at,
                        t("hub.detail.code.just_now")
                      )}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {code.tree?.readme ? (
          <section className="overflow-hidden border border-border bg-card">
            <div className="border-b border-border bg-muted/40 px-3 py-2 text-xs font-semibold text-foreground">
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

        <section className="border border-border bg-card p-4">
          <h3 className="mb-1.5 text-xs font-semibold text-foreground">
            {t("hub.detail.code.sidebar_description")}
          </h3>
          <p className="text-xs leading-relaxed text-muted-foreground">
            {code.summary?.description || t("hub.detail.code.no_description")}
          </p>
        </section>
      </div>

      <aside className="w-full shrink-0 space-y-5 lg:w-60">
        {code.summary?.size_kib != null ? (
          <ul className="space-y-1.5 text-xs text-muted-foreground">
            <li className="inline-flex items-center gap-1.5">
              <HardDrive aria-hidden className="size-3.5" />
              {t("hub.detail.code.size", { size: code.summary.size_kib })}
            </li>
          </ul>
        ) : null}

        {languages.length > 0 ? (
          <div>
            <h3 className="mb-2 text-xs font-semibold text-foreground">
              {t("hub.detail.code.languages")}
            </h3>
            <div className="mb-2 flex h-2.5 overflow-hidden rounded-sm bg-muted">
              {languages.map((lang) => (
                <span
                  key={lang.name}
                  className="h-full"
                  style={{
                    width: `${lang.percent}%`,
                    backgroundColor: languageColor(lang.name),
                  }}
                  title={`${lang.name} ${lang.percent}%`}
                />
              ))}
            </div>
            <ul className="space-y-1">
              {languages.map((lang) => (
                <li
                  key={lang.name}
                  className="flex items-center gap-2 text-xs text-foreground"
                >
                  <span
                    aria-hidden
                    className="size-2 shrink-0 rounded-full"
                    style={{ backgroundColor: languageColor(lang.name) }}
                  />
                  <span className="font-medium">{lang.name}</span>
                  <span className="text-muted-foreground">{lang.percent}%</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </aside>
    </div>
  );
}
