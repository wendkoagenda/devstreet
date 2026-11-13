import { useTranslation } from "react-i18next";
import { CodeBrowser } from "./code-browser";
export { PresentationPanel } from "./project-presentation";

interface CodePanelProps {
  projectId: number;
  projectTitle: string;
  isOwner: boolean;
  repositoryReady: boolean;
  namespace?: string | null;
  repoName?: string | null;
}

export function CodePanel({
  projectId,
  projectTitle,
  isOwner,
  repositoryReady,
  namespace,
  repoName,
}: CodePanelProps) {
  const { t } = useTranslation();

  if (!repositoryReady) {
    return (
      <section className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-card sm:p-6">
        <h2 className="text-sm font-bold text-foreground">{t("hub.detail.code.title")}</h2>
        <p className="rounded-lg border border-dashed border-border bg-secondary/60 px-3 py-3 text-xs text-muted-foreground">
          {t("hub.detail.code.not_ready")}
        </p>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-3">
      <CodeBrowser
        projectId={projectId}
        projectTitle={projectTitle}
        isOwner={isOwner}
        namespaceHint={namespace}
        repoNameHint={repoName}
      />
    </section>
  );
}
