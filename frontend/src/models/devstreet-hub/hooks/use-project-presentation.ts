import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { useLazyGetAnalysisQuery, useSavePresentationMutation, useSetAiConsentMutation, useSuggestPresentationMutation } from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type { Analysis, Project } from "../schema";

export type PresentationSuggestion = {
  description: string;
  references: { source_id: string; line_start: number; line_end: number; reason: string }[];
  unknowns: string[];
};

export function suggestionOf(analysis: Analysis | null): PresentationSuggestion | null {
  const raw = analysis?.result as Partial<PresentationSuggestion> | undefined;
  if (analysis?.status !== "succeeded" || typeof raw?.description !== "string") return null;
  return { description: raw.description, references: raw.references ?? [], unknowns: raw.unknowns ?? [] };
}

export function useProjectPresentation(project: Project) {
  const { t, i18n } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [description, setDescription] = useState(project.description);
  const [problem, setProblem] = useState(project.problem);
  const [baseUpdatedAt, setBaseUpdatedAt] = useState(project.updated_at);
  const [files, setFiles] = useState<File[]>([]);
  const [removed, setRemoved] = useState<number[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [consent, setConsent] = useState(Boolean(project.ai_consent_at));
  const [draftAtRequest, setDraftAtRequest] = useState("");
  const epoch = useRef(0);
  const [save, saving] = useSavePresentationMutation();
  const [suggest] = useSuggestPresentationMutation();
  const [fetchAnalysis] = useLazyGetAnalysisQuery();
  const [setAiConsent, consentState] = useSetAiConsentMutation();
  useEffect(() => () => { epoch.current += 1; }, []);

  const begin = () => {
    epoch.current += 1;
    setDescription(project.description); setProblem(project.problem);
    setBaseUpdatedAt(project.updated_at); setFiles([]); setRemoved([]);
    setAnalysis(null); setError(""); setGenerating(false);
    setConsent(Boolean(project.ai_consent_at)); setEditing(true);
  };
  const cancel = () => {
    epoch.current += 1;
    setGenerating(false); setEditing(false); setFiles([]); setRemoved([]); setAnalysis(null);
  };
  const mapError = (reason: unknown) => {
    const status = httpStatusOf(reason);
    return status === 429 ? t("hub.presentation.quota")
      : status === 503 ? t("hub.presentation.unavailable")
      : status === 409 ? (apiDetailOf(reason) || t("hub.presentation.conflict"))
      : apiDetailOf(reason) || t("hub.presentation.failed");
  };
  const saveChanges = async () => {
    const body = new FormData();
    body.append("description", description); body.append("problem", problem);
    body.append("base_updated_at", baseUpdatedAt);
    files.forEach(file => body.append("images", file));
    removed.forEach(id => body.append("remove_image_ids", String(id)));
    try {
      await save({ projectId: project.id, body }).unwrap();
      toast.success(t("hub.detail.toasts.presentation_saved")); cancel();
    } catch (reason) { setError(mapError(reason)); }
  };
  const addFiles = (incoming: File[]) => {
    if (files.length + (project.images?.length ?? 0) - removed.length + incoming.length > 4) {
      setError(t("hub.presentation.image_limit")); return;
    }
    if (incoming.some(file => !["image/jpeg", "image/png", "image/webp"].includes(file.type) || file.size > 4 * 1024 * 1024)) {
      setError(t("hub.presentation.image_invalid")); return;
    }
    setError(""); setFiles(current => [...current, ...incoming]);
  };
  const toggleConsent = async (enabled: boolean) => {
    setError("");
    try {
      const updated = await setAiConsent({ projectId: project.id, enabled }).unwrap();
      setConsent(enabled);
      if (updated.description !== project.description || updated.problem !== project.problem) {
        setError(t("hub.presentation.conflict"));
      } else { setBaseUpdatedAt(updated.updated_at); }
      if (!enabled) { epoch.current += 1; setGenerating(false); setAnalysis(null); }
    } catch (reason) { setError(mapError(reason)); }
  };
  const generate = async () => {
    if (!consent) return;
    const version = ++epoch.current;
    setGenerating(true); setError(""); setAnalysis(null); setDraftAtRequest(description);
    try {
      let next = await suggest({ projectId: project.id, description, language: i18n.language.startsWith("fr") ? "fr" : "en" }).unwrap();
      for (let attempt = 0; ; attempt += 1) {
        if (version !== epoch.current) return;
        setAnalysis(next);
        if (next.status === "succeeded") {
          if (!suggestionOf(next)) throw new Error("invalid_result");
          break;
        }
        if (next.status === "failed") throw new Error("analysis_failed");
        if (attempt >= 23) { setError(t("hub.presentation.timeout")); break; }
        await new Promise(resolve => window.setTimeout(resolve, Math.min(8000, 1500 * (attempt + 1))));
        if (version !== epoch.current) return;
        next = await fetchAnalysis(next.id).unwrap();
      }
    } catch (reason) { if (version === epoch.current) setError(mapError(reason)); }
    finally { if (version === epoch.current) setGenerating(false); }
  };
  return {
    editing, begin, cancel, description, setDescription, problem, setProblem,
    files, setFiles, removed, setRemoved, addFiles, saveChanges, saving: saving.isLoading,
    consent, toggleConsent, consentBusy: consentState.isLoading, generate, generating,
    analysis, suggestion: suggestionOf(analysis), clearSuggestion: () => setAnalysis(null),
    draftChanged: description !== draftAtRequest && description !== suggestionOf(analysis)?.description, error,
  };
}
