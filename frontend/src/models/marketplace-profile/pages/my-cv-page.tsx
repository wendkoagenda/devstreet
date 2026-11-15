import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Download, Settings2, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { useAuthSlice } from "@/models/auth/slice";
import { useGetPublicProfileQuery } from "@/models/marketplace-network/api";
import { useUpdateMyProfilMutation } from "@/models/marketplace-space/api";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { CV_VISIBILITIES } from "@/models/marketplace-space/options";
import { CvStatsStrip } from "@/models/marketplace-stats/components/page-stats";
import {
  useGetMyCvSettingsQuery,
  useResetMyCvSettingsMutation,
  useUpdateMyCvSettingsMutation,
} from "../api";
import { CvDocument } from "../components/cv-document";
import { CvSettingsSheet } from "../components/cv-settings-sheet";
import { cvPalette, sameSettings, type CvSettings } from "../cv-settings";
import { downloadCv } from "../download-cv";

function MyCvContent() {
  const { t } = useTranslation();
  const { profil } = useMySpace();
  const user = useAuthSlice((state) => state.user);
  const { data: profile, isLoading } = useGetPublicProfileQuery(profil?.id ?? 0, { skip: !profil });
  const { data: cvSettings, isLoading: settingsLoading } = useGetMyCvSettingsQuery();
  const [updateProfil, { isLoading: visibilitySaving }] = useUpdateMyProfilMutation();
  const [updateSettings, { isLoading: saving }] = useUpdateMyCvSettingsMutation();
  const [resetSettings, { isLoading: resetting }] = useResetMyCvSettingsMutation();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [downloading, setDownloading] = useState(false);
  // Réglages en cours de modification (null : on affiche ceux qui sont enregistrés)
  const [draft, setDraft] = useState<CvSettings | null>(null);

  const saved = cvSettings?.settings;
  const settings = draft ?? saved;
  const dirty = Boolean(draft && saved && !sameSettings(draft, saved));
  const palette = useMemo(
    () => (settings && cvSettings ? cvPalette(settings, cvSettings.presets) : null),
    [settings, cvSettings],
  );
  const visibilityLabel = CV_VISIBILITIES.find(
    (option) => option.value === profil?.cv_visibility
  )?.label;

  const change = (changes: Partial<CvSettings>) => {
    if (settings) setDraft({ ...settings, ...changes });
  };

  const save = async () => {
    if (!draft) return;
    try {
      await updateSettings(draft).unwrap();
      setDraft(null);
      CreationSuccessSonner(t("marketplace.cv.style_saved"));
    } catch {
      CreationErrorSonner(t("marketplace.cv.style_save_error"));
    }
  };

  const reset = async () => {
    try {
      await resetSettings().unwrap();
      setDraft(null);
      CreationSuccessSonner(t("marketplace.cv.style_reset"));
    } catch {
      CreationErrorSonner(t("marketplace.cv.style_reset_error"));
    }
  };

  const changeVisibility = async (value: string) => {
    try {
      await updateProfil({ cv_visibility: value }).unwrap();
      CreationSuccessSonner(t("marketplace.cv.visibility_updated"));
    } catch {
      CreationErrorSonner(t("marketplace.cv.visibility_error"));
    }
  };

  const download = async () => {
    setDownloading(true);
    try {
      // Le PDF suit ce que montre l'aperçu, même si le style n'est pas encore enregistré
      await downloadCv(undefined, dirty && draft ? draft : undefined);
    } catch {
      CreationErrorSonner(t("marketplace.cv_download_error"));
    } finally {
      setDownloading(false);
    }
  };

  const photo = user?.photo ? buildMediaUrl(user.photo) : null;

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4">
      <CvStatsStrip />

      <div className="flex flex-col gap-4 rounded-xl border border-border bg-card p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 flex-col gap-1">
          <div className="flex flex-wrap items-center gap-1.5">
            <h1 className="text-lg font-semibold text-foreground">
              {t("marketplace.cv.title")}
            </h1>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-8"
              aria-label={t("marketplace.cv.settings_aria")}
              title={t("marketplace.cv.settings_title")}
              onClick={() => setSettingsOpen(true)}
              disabled={!cvSettings}
            >
              <Settings2 className="size-4" />
            </Button>
            {dirty ? (
              <Badge variant="outline" className="ml-1 gap-1 font-normal">
                <Sparkles className="size-3" />
                {t("marketplace.cv.unsaved_preview")}
              </Badge>
            ) : null}
          </div>
          <p className="text-sm text-muted-foreground">
            {t("marketplace.cv.sub")}
            {visibilityLabel
              ? ` ${t("marketplace.cv.visible_by", {
                  who: visibilityLabel.toLowerCase(),
                })}`
              : ""}
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          {dirty ? (
            <>
              <Button type="button" variant="ghost" onClick={() => setDraft(null)}>
                {t("actions.cancel")}
              </Button>
              <Button type="button" variant="outline" onClick={save} disabled={saving}>
                {t("marketplace.cv.save_style")}
              </Button>
            </>
          ) : null}
          <Button type="button" disabled={downloading} onClick={download}>
            <Download className="size-4" />
            {t("marketplace.cv.download_pdf")}
          </Button>
        </div>
      </div>

      <div className="rounded-xl bg-muted/60 p-3 sm:p-8">
        {!isLoading && !settingsLoading && profile && settings && palette ? (
          <>
            <CvDocument
              profile={profile}
              phone={profil?.phone}
              photoUrl={photo}
              settings={settings}
              palette={palette}
            />
            {profile.experiences.length === 0 ? (
              <p className="mt-4 text-center text-xs text-muted-foreground">
                {t("marketplace.cv.no_experience")}{" "}
                <Link to="/profil/me?section=dev" className="underline">
                  {t("marketplace.cv.add_experience")}
                </Link>
                .
              </p>
            ) : null}
          </>
        ) : (
          <Skeleton className="mx-auto aspect-[210/297] w-full max-w-[794px]" />
        )}
      </div>

      {cvSettings && settings ? (
        <CvSettingsSheet
          open={settingsOpen}
          onOpenChange={setSettingsOpen}
          settings={settings}
          presets={cvSettings.presets}
          sections={cvSettings.sections}
          onChange={change}
          dirty={dirty}
          saving={saving || resetting}
          onSave={save}
          onDiscard={() => setDraft(null)}
          onReset={reset}
          visibility={profil?.cv_visibility}
          onVisibilityChange={changeVisibility}
          visibilitySaving={visibilitySaving}
        />
      ) : null}
    </div>
  );
}

/** Mon CV : aperçu du CV automatique au format A4, personnalisation du style, visibilité et téléchargement PDF. */
export default function MyCvPage() {
  return (
    <RequireProfil>
      <MyCvContent />
    </RequireProfil>
  );
}
