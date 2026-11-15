import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { BookOpen, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import {
  GUIDE_SECTIONS,
  guideFileUrl,
  isKnownGuideSlug,
} from "../manifest";

/** Réécrit les liens relatifs .md du guide vers des routes /aide/... */
function resolveGuideHref(href: string | undefined, currentSlug: string): string | undefined {
  if (!href) return href;
  if (
    href.startsWith("http://") ||
    href.startsWith("https://") ||
    href.startsWith("mailto:") ||
    href.startsWith("#")
  ) {
    return href;
  }
  if (href.startsWith("/aide")) return href;

  const withoutHash = href.split("#")[0] ?? href;
  const hash = href.includes("#") ? `#${href.split("#")[1]}` : "";
  let target = withoutHash.replace(/^\.\//, "").replace(/\.md$/i, "");

  if (target.startsWith("../")) {
    const baseParts = currentSlug.split("/").slice(0, -1);
    const relParts = target.split("/");
    for (const part of relParts) {
      if (part === "..") baseParts.pop();
      else if (part && part !== ".") baseParts.push(part);
    }
    target = baseParts.join("/");
  } else if (target.includes("/")) {
    // chemin déjà relatif au dossier courant du fichier (ex. forum/fil depuis index forum)
    if (!target.startsWith("forum/") && !target.startsWith("marketplace/") &&
        !target.startsWith("projets/") && !target.startsWith("administration/") &&
        !target.startsWith("compte/") && currentSlug.includes("/")) {
      const dir = currentSlug.split("/").slice(0, -1).join("/");
      target = `${dir}/${target}`;
    }
  } else if (currentSlug.includes("/")) {
    const dir = currentSlug.split("/").slice(0, -1).join("/");
    target = `${dir}/${target}`;
  }

  if (target === "index" || target.endsWith("/index")) {
    target = target === "index" ? "index" : target.replace(/\/index$/, "/index");
  }

  // Liens vers docs/ hors guide public : laisser en texte brut
  if (target.includes("docs/") || target.startsWith("../../../")) {
    return undefined;
  }

  const path =
    `/aide/${target === "index" ? "" : target}`.replace(/\/$/, "") || "/aide";
  return `${path}${hash}`;
}

function GuideContent({ slug }: { slug: string }) {
  const { t } = useTranslation();
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setMarkdown(null);
    setError(false);
    fetch(guideFileUrl(slug))
      .then(async (response) => {
        if (!response.ok) throw new Error("missing");
        return response.text();
      })
      .then((text) => {
        if (!cancelled) setMarkdown(text);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (error) {
    return (
      <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
        {t("guide.load_error")}
      </p>
    );
  }
  if (markdown === null) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-4/6" />
      </div>
    );
  }

  return (
    <article className="guide-prose max-w-3xl text-sm leading-relaxed text-foreground">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="mb-4 text-2xl font-semibold tracking-tight">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="mb-3 mt-8 text-lg font-semibold">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-2 mt-6 text-base font-semibold">{children}</h3>
          ),
          p: ({ children }) => <p className="mb-3 text-muted-foreground">{children}</p>,
          ul: ({ children }) => (
            <ul className="mb-4 list-disc space-y-1 pl-5 text-muted-foreground">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-4 list-decimal space-y-1 pl-5 text-muted-foreground">{children}</ol>
          ),
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          a: ({ href, children }) => {
            const resolved = resolveGuideHref(href, slug);
            if (!resolved) {
              return <span className="font-medium text-foreground">{children}</span>;
            }
            if (resolved.startsWith("/aide")) {
              return (
                <Link
                  to={resolved === "/aide" ? "/aide" : resolved}
                  className="font-medium text-brand-strong underline-offset-2 hover:underline"
                >
                  {children}
                </Link>
              );
            }
            return (
              <a
                href={resolved}
                className="font-medium text-brand-strong underline-offset-2 hover:underline"
                target={resolved.startsWith("http") ? "_blank" : undefined}
                rel={resolved.startsWith("http") ? "noopener noreferrer" : undefined}
              >
                {children}
              </a>
            );
          },
          table: ({ children }) => (
            <div className="mb-4 overflow-x-auto rounded-lg border border-border">
              <table className="w-full min-w-[28rem] border-collapse text-left text-xs">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-muted/60">{children}</thead>,
          th: ({ children }) => (
            <th className="border-b border-border px-3 py-2 font-semibold text-foreground">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-b border-border px-3 py-2 text-muted-foreground">{children}</td>
          ),
          code: ({ className, children }) => {
            const block = Boolean(className);
            if (block) {
              return (
                <code className="block overflow-x-auto rounded-lg bg-muted p-3 font-mono text-xs text-foreground">
                  {children}
                </code>
              );
            }
            return (
              <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.8rem] text-foreground">
                {children}
              </code>
            );
          },
          pre: ({ children }) => <pre className="mb-4 overflow-x-auto">{children}</pre>,
          blockquote: ({ children }) => (
            <blockquote className="mb-4 border-l-2 border-brand pl-3 text-muted-foreground">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-8 border-border" />,
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">{children}</strong>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </article>
  );
}

/** Guide utilisateur intégré : sommaire par module + contenu Markdown (Zensical / public/guide). */
export default function GuidePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const params = useParams();
  const raw = params["*"];
  const slug = useMemo(() => {
    if (!raw || raw === "" || raw === "index") return "index";
    return raw.replace(/\/$/, "");
  }, [raw]);

  useEffect(() => {
    if (!isKnownGuideSlug(slug)) {
      navigate("/aide", { replace: true });
    }
  }, [slug, navigate]);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 lg:flex-row lg:items-start">
      <aside className="w-full shrink-0 lg:sticky lg:top-4 lg:w-64">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
          <BookOpen className="size-4" aria-hidden />
          {t("guide.title")}
        </div>
        <nav aria-label={t("guide.nav_aria")} className="flex flex-col gap-4">
          {GUIDE_SECTIONS.map((section) => (
            <div key={section.id}>
              <p className="mb-1 px-2 font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
                {t(section.titleKey)}
              </p>
              <ul className="space-y-0.5">
                {section.pages.map((page) => {
                  const active = page.slug === slug;
                  const to = page.slug === "index" ? "/aide" : `/aide/${page.slug}`;
                  return (
                    <li key={page.slug}>
                      <Link
                        to={to}
                        className={cn(
                          "flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm transition-colors",
                          active
                            ? "bg-brand-soft font-medium text-brand-strong"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                        aria-current={active ? "page" : undefined}
                      >
                        <ChevronRight
                          className={cn("size-3.5 shrink-0", active ? "opacity-100" : "opacity-0")}
                          aria-hidden
                        />
                        <span className="truncate">{t(page.titleKey)}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
      </aside>

      <div className="min-w-0 flex-1 rounded-xl border border-border bg-card p-5 sm:p-8">
        <GuideContent slug={isKnownGuideSlug(slug) ? slug : "index"} />
      </div>
    </div>
  );
}
