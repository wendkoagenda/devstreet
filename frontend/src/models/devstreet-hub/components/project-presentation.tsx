import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { ArrowRight, Check, Code2, FileText, Globe2, ImagePlus, Loader2, Pencil, Scale, ShieldCheck, Sparkles, Users, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { API_V1_URL } from "@/helpers/api/csrf";
import type { Project, ProjectDetailTab, Technology } from "../schema";
import { useProjectPresentation } from "../hooks/use-project-presentation";

const card = "rounded-2xl border border-border bg-card shadow-card";
const iconBox = "flex size-11 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand";

function Initials({ name }: { name: string }) {
  const initials = name.trim().split(/\s+/).slice(0, 2).map(part => part[0]).join("").toUpperCase();
  return <span aria-hidden className="flex size-11 shrink-0 items-center justify-center rounded-full bg-brand font-semibold text-brand-foreground">{initials || "DS"}</span>;
}

function LocalPreview({ file }: { file: File }) {
  const [url, setUrl] = useState("");
  useEffect(() => {
    const next = URL.createObjectURL(file); setUrl(next);
    return () => URL.revokeObjectURL(next);
  }, [file]);
  return url ? <img src={url} alt={file.name} className="h-28 w-full rounded-lg object-cover" /> : null;
}

function Paragraphs({ text }: { text: string }) {
  return <div className="space-y-5 text-sm leading-7 text-foreground/90 sm:text-[15px]">
    {text.split(/\n\s*\n/).filter(part => part.trim()).map((part, index) => <p key={index} className="whitespace-pre-wrap break-words">{part}</p>)}
  </div>;
}

interface Props {
  project: Project;
  canEdit: boolean;
  canAnalyze?: boolean;
  technologies?: Technology[];
  onNavigate?: (tab: ProjectDetailTab) => void;
}

export function PresentationPanel({ project, canEdit, canAnalyze = false, technologies = [], onNavigate }: Props) {
  const { t } = useTranslation();
  const edit = useProjectPresentation(project);
  const owner = project.owner_display_name || t("hub.presentation.project_owner");
  const images = project.images ?? [];
  const imageUrl = (id: number) => `${API_V1_URL}/projects/${project.id}/presentation/images/${id}`;
  const repositoryReady = project.repository?.status === "ready";
  const keptImages = images.filter(image => !edit.removed.includes(image.id));

  if (edit.editing && canEdit) return (
    <section aria-labelledby="presentation-edit-title" className="space-y-5">
      <div className="flex items-center gap-3">
        <span className={iconBox}><Pencil aria-hidden className="size-5" /></span>
        <div><h2 id="presentation-edit-title" className="text-xl font-semibold tracking-tight text-foreground">{t("hub.presentation.edit_title")}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{t("hub.presentation.edit_hint")}</p></div>
      </div>
      {edit.error ? <p role="alert" className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">{edit.error}</p> : null}
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.9fr)]">
        <form className={`${card} min-w-0 p-5 sm:p-6`} onSubmit={event => { event.preventDefault(); void edit.saveChanges(); }}>
          <div className="mb-5 flex flex-col items-start gap-2">
            <Button type="button" variant="outline" disabled={!canAnalyze || !edit.consent || !repositoryReady || edit.generating || edit.saving || edit.consentBusy} onClick={() => void edit.generate()} className="h-auto min-h-10 gap-2 whitespace-normal border-brand-soft-border text-left text-brand hover:bg-brand-soft">
              {edit.generating ? <Loader2 aria-hidden className="size-4 shrink-0 animate-spin" /> : <Sparkles aria-hidden className="size-4 shrink-0" />}
              {t(edit.generating ? "hub.presentation.analyzing" : "hub.presentation.improve")}
            </Button>
            <p className="text-xs leading-5 text-muted-foreground">{t(!canAnalyze ? "hub.presentation.no_ai_permission" : !repositoryReady ? "hub.presentation.repository_needed" : "hub.presentation.ai_hint")}</p>
          </div>
          <Label htmlFor="project-description" className="text-sm font-semibold">{t("hub.presentation.description_label")}</Label>
          <Textarea id="project-description" value={edit.description} onChange={event => edit.setDescription(event.target.value)} maxLength={10000} rows={11} disabled={edit.saving} placeholder={t("hub.presentation.placeholder")} className="mt-2 min-h-64 resize-y rounded-xl text-sm leading-7" />
          <div className="mt-2 flex justify-between gap-3 text-xs text-muted-foreground"><span>{t("hub.presentation.free_text")}</span><span className="shrink-0 tabular-nums">{edit.description.length}/10 000</span></div>
          <details className="mt-5 rounded-xl border border-border px-4 py-3">
            <summary className="cursor-pointer text-xs font-medium text-muted-foreground">{t("hub.presentation.short_summary")}</summary>
            <Label htmlFor="project-problem" className="sr-only">{t("hub.detail.presentation.problem_label")}</Label>
            <Textarea id="project-problem" value={edit.problem} onChange={event => edit.setProblem(event.target.value)} maxLength={2000} rows={3} disabled={edit.saving} className="mt-3 text-sm" />
          </details>
          <div className="mt-6 border-t border-border pt-5">
            <p className="mb-3 text-sm font-semibold">{t("hub.presentation.images_label")} <span className="font-normal text-muted-foreground">· {t("hub.presentation.optional")}</span></p>
            <div className="flex flex-wrap items-center gap-3">
              <Label htmlFor="presentation-images" className={`inline-flex min-h-10 items-center gap-2 rounded-lg border border-border px-3 text-sm font-medium ${edit.saving ? "pointer-events-none opacity-50" : "cursor-pointer hover:bg-muted"}`}><ImagePlus aria-hidden className="size-4" />{t("hub.presentation.add_images")}</Label>
              <input id="presentation-images" type="file" accept="image/jpeg,image/png,image/webp" multiple disabled={edit.saving} className="sr-only" onChange={event => { edit.addFiles(Array.from(event.target.files ?? [])); event.target.value = ""; }} />
              <span className="text-xs text-muted-foreground">{t("hub.presentation.image_help")}</span>
            </div>
            {keptImages.length || edit.files.length ? <div className="mt-4 grid grid-cols-2 gap-3">
              {keptImages.map(image => <div key={image.id} className="relative"><img src={imageUrl(image.id)} alt={image.display_name} className="h-28 w-full rounded-lg object-cover" /><Button type="button" variant="secondary" size="icon" disabled={edit.saving} aria-label={t("hub.presentation.remove_image", { name: image.display_name })} className="absolute right-1 top-1 size-7 shadow-sm" onClick={() => edit.setRemoved(current => [...current, image.id])}><X className="size-3.5" /></Button></div>)}
              {edit.files.map((file, index) => <div key={`${index}-${file.name}`} className="relative"><LocalPreview file={file} /><Button type="button" variant="secondary" size="icon" disabled={edit.saving} aria-label={t("hub.presentation.remove_image", { name: file.name })} className="absolute right-1 top-1 size-7 shadow-sm" onClick={() => edit.setFiles(current => current.filter((_, i) => i !== index))}><X className="size-3.5" /></Button></div>)}
            </div> : null}
          </div>
          <div className="mt-6 flex flex-wrap justify-end gap-2 border-t border-border pt-5">
            <Button type="button" variant="outline" disabled={edit.saving || edit.consentBusy} onClick={edit.cancel}>{t("common.cancel")}</Button>
            <Button type="submit" disabled={edit.saving || edit.consentBusy} className="gap-2">{edit.saving ? <Loader2 aria-hidden className="size-4 animate-spin" /> : null}{t("hub.presentation.save")}</Button>
          </div>
        </form>
        <aside className="min-w-0 space-y-4" aria-label={t("hub.presentation.ai_title")}>
          {canAnalyze ? <div className="rounded-xl border border-border p-4">
            <div className="flex items-start gap-3"><Checkbox id="presentation-consent" checked={edit.consent} disabled={edit.consentBusy || edit.saving} onCheckedChange={checked => void edit.toggleConsent(checked === true)} /><Label htmlFor="presentation-consent" className="text-xs leading-5">{t("hub.presentation.consent")}</Label></div>
          </div> : null}
          <div className={`${card} overflow-hidden`} aria-busy={edit.generating}>
            <div className="flex items-center justify-between gap-3 border-b border-brand-soft-border bg-brand-soft p-4 text-brand"><h3 className="flex items-center gap-2 font-semibold"><Sparkles aria-hidden className="size-5" />{t("hub.presentation.ai_title")}</h3><span className="rounded-full bg-card px-2 py-1 text-[10px] font-medium">{t("hub.presentation.review")}</span></div>
            <div className="space-y-5 p-5">
              {edit.generating ? <div role="status" className="flex gap-3 py-8 text-sm text-muted-foreground"><Loader2 aria-hidden className="size-5 shrink-0 animate-spin text-brand" />{t(edit.analysis?.status === "queued" ? "hub.presentation.queued" : "hub.presentation.analyzing")}</div> : edit.suggestion ? <>
                <Paragraphs text={edit.suggestion.description} />
                <div className="space-y-2 border-t border-border pt-4 text-xs text-muted-foreground">
                  <p className="flex items-center gap-2"><FileText aria-hidden className="size-4" />{t("hub.presentation.sources")}</p>
                  {edit.suggestion.references.map((ref, index) => {
                    const source = edit.analysis?.sources.find(item => item.source_id === ref.source_id);
                    return <button key={index} type="button" className="block max-w-full break-all text-left text-brand underline-offset-4 hover:underline" onClick={() => {
                      if (source && edit.analysis) window.open(`/hub/projects/${project.id}?tab=code&mode=blob&ref=${encodeURIComponent(edit.analysis.commit_sha)}&path=${encodeURIComponent(source.path)}`, "_blank", "noopener,noreferrer");
                    }}>{source?.path || ref.source_id} · L{ref.line_start}–{ref.line_end}</button>;
                  })}
                  <p>{t("hub.presentation.version")} <span className="font-mono">{edit.analysis?.commit_sha.slice(0, 10)}</span></p>
                  {project.repository?.current_sha && project.repository.current_sha !== edit.analysis?.commit_sha ? <p className="text-warning">{t("hub.presentation.stale")}</p> : null}
                  {edit.suggestion.unknowns.map((unknown, index) => <p key={index}>{unknown}</p>)}
                  <p>{t("hub.presentation.verify")}</p>
                </div>
                {edit.draftChanged ? <p className="text-xs text-warning">{t("hub.presentation.draft_changed")}</p> : null}
                <div className="flex flex-wrap gap-2"><Button type="button" disabled={edit.saving} className="gap-2 bg-brand text-brand-foreground hover:bg-brand-strong" onClick={() => edit.setDescription(edit.suggestion!.description)}><Check aria-hidden className="size-4" />{t("hub.presentation.apply")}</Button><Button type="button" variant="ghost" onClick={edit.clearSuggestion}>{t("hub.presentation.ignore")}</Button></div>
              </> : <div className="py-8 text-center"><span className={`${iconBox} mx-auto mb-4`}><FileText aria-hidden className="size-5" /></span><p className="text-sm leading-6 text-muted-foreground">{t("hub.presentation.ai_empty")}</p></div>}
              <p className="rounded-xl bg-brand-soft p-3 text-xs leading-5 text-brand">{t("hub.presentation.not_published")}</p>
            </div>
          </div>
        </aside>
      </div>
      <p className="flex items-start gap-2 rounded-xl border border-border bg-muted/50 p-4 text-xs leading-5 text-muted-foreground"><ShieldCheck aria-hidden className="size-4 shrink-0" />{t("hub.presentation.unchanged")}</p>
    </section>
  );

  return <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
    <div className="min-w-0 space-y-5">
      <article className={`${card} overflow-hidden`}>
        <div className="flex items-center justify-between gap-3 border-b border-border p-5 sm:px-6"><div className="flex min-w-0 items-center gap-3"><Initials name={owner} /><div className="min-w-0"><h2 className="truncate text-sm font-semibold text-foreground">{owner}</h2><p className="mt-0.5 text-xs text-muted-foreground">{t("hub.presentation.project_owner")}</p></div></div>
          {canEdit ? <Button type="button" variant="outline" onClick={edit.begin} className="shrink-0 gap-2 text-xs"><Pencil aria-hidden className="size-3.5" />{t("hub.presentation.edit")}</Button> : null}
        </div>
        <div className="space-y-5 p-5 sm:p-6">
          <h3 className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{t("hub.presentation.title")}</h3>
          {project.description.trim() ? <Paragraphs text={project.description} /> : <div className="rounded-xl border border-dashed border-border p-6 text-sm leading-6 text-muted-foreground"><FileText aria-hidden className="mb-3 size-6" />{t(canEdit ? "hub.presentation.empty_owner" : "hub.presentation.empty")}{canEdit ? <Button type="button" variant="outline" className="mt-4 block" onClick={edit.begin}>{t("hub.presentation.write")}</Button> : null}</div>}
          {images.length ? <div className={`grid gap-3 ${images.length > 1 ? "sm:grid-cols-2" : ""}`}>{images.map(image => <a key={image.id} href={imageUrl(image.id)} target="_blank" rel="noopener noreferrer" className="overflow-hidden rounded-xl border border-border bg-muted"><img src={imageUrl(image.id)} alt={image.display_name} loading="lazy" className="max-h-80 w-full object-contain" /></a>)}</div> : null}
          <p className="flex items-center gap-2 border-t border-border pt-4 text-xs text-muted-foreground"><FileText aria-hidden className="size-4" />{t("hub.presentation.author_note")}</p>
        </div>
      </article>
      <section className={`${card} flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between`}><div className="flex items-center gap-3"><span className={iconBox}><Users aria-hidden className="size-5" /></span><div><h3 className="text-sm font-semibold">{t("hub.presentation.contribute_title")}</h3><p className="mt-1 text-xs leading-5 text-muted-foreground">{t("hub.presentation.contribute_hint")}</p></div></div><div className="flex flex-wrap gap-2"><Button type="button" onClick={() => onNavigate?.("contribute")} className="text-xs">{t("hub.presentation.tasks")}</Button><Button type="button" variant="outline" onClick={() => onNavigate?.("code")} className="gap-2 text-xs"><Code2 aria-hidden className="size-4" />{t("hub.presentation.code")}</Button></div></section>
    </div>
    <aside className="space-y-5">
      <section className={`${card} p-5`}><h3 className="mb-4 text-base font-semibold">{t("hub.presentation.about")}</h3><div className="flex items-center gap-3 border-b border-border pb-4"><Initials name={owner} /><span className="break-words text-sm font-medium">{owner}</span></div><dl className="divide-y divide-border text-xs"><div className="flex justify-between gap-3 py-4"><dt className="flex items-center gap-2 text-muted-foreground"><Scale aria-hidden className="size-4" />{t("hub.presentation.license")}</dt><dd>{project.declared_license}</dd></div><div className="flex justify-between gap-3 py-4"><dt className="flex items-center gap-2 text-muted-foreground"><Globe2 aria-hidden className="size-4" />{t("hub.presentation.visibility")}</dt><dd>{t(`hub.status.${project.status}`)}</dd></div>{technologies.length ? <div className="pt-4"><dt className="mb-3 text-muted-foreground">{t("hub.presentation.technologies")}</dt><dd className="flex flex-wrap gap-1.5">{technologies.map(tech => <span key={tech.id} className="rounded-md border border-border bg-muted px-2 py-1 text-[11px]">{tech.label}</span>)}</dd></div> : null}</dl></section>
      <section className={`${card} p-5`}><h3 className="mb-3 text-sm font-semibold">{t("hub.presentation.shortcuts")}</h3>{([{ tab: "code", label: "code", icon: Code2 }, { tab: "contribute", label: "tasks", icon: FileText }, { tab: "team", label: "team", icon: Users }] as const).map(item => <button key={item.tab} type="button" className="flex min-h-11 w-full items-center gap-3 border-b border-border py-3 text-left text-xs last:border-0 hover:text-brand" onClick={() => onNavigate?.(item.tab)}><item.icon aria-hidden className="size-4" />{t(`hub.presentation.${item.label}`)}<ArrowRight aria-hidden className="ml-auto size-3.5" /></button>)}</section>
    </aside>
  </div>;
}
