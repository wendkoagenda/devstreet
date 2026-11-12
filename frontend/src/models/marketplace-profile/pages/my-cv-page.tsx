import { useState } from "react";
import { Link } from "react-router-dom";
import { Download } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { useGetPublicProfileQuery } from "@/models/marketplace-network/api";
import { formatDate } from "@/models/marketplace-offers/labels";
import { useUpdateMyProfilMutation } from "@/models/marketplace-space/api";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { CV_VISIBILITIES } from "@/models/marketplace-space/options";
import { downloadCv } from "../download-cv";

function MyCvContent() {
  const { profil } = useMySpace();
  const { data, isLoading } = useGetPublicProfileQuery(profil?.id ?? 0, { skip: !profil });
  const [updateProfil, { isLoading: isSaving }] = useUpdateMyProfilMutation();
  const [downloading, setDownloading] = useState(false);

  const download = async () => {
    setDownloading(true);
    try {
      await downloadCv();
    } catch {
      CreationErrorSonner("Impossible de télécharger le CV");
    } finally {
      setDownloading(false);
    }
  };

  const changeVisibility = async (value: string) => {
    try {
      await updateProfil({ cv_visibility: value }).unwrap();
      CreationSuccessSonner("Visibilité du CV mise à jour");
    } catch {
      CreationErrorSonner("Impossible de modifier la visibilité");
    }
  };

  return (
    <div className="mx-auto grid w-full max-w-5xl items-start gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
      <Card>
        <CardContent className="flex flex-col gap-5 p-8">
          {isLoading || !data ? (
            <Skeleton className="h-72 w-full" />
          ) : (
            <>
              <div className="flex flex-col gap-1 border-b border-border pb-4">
                <span className="text-xl font-semibold text-foreground">{data.name}</span>
                <span className="text-sm text-muted-foreground">
                  {[data.headline, data.city].filter(Boolean).join(" · ")}
                </span>
                <span className="text-xs text-muted-foreground">
                  {[data.email, data.github_url, data.linkedin_url, data.portfolio_url]
                    .filter(Boolean)
                    .join(" · ")}
                </span>
              </div>
              {data.bio ? (
                <section className="flex flex-col gap-1">
                  <h2 className="text-sm font-semibold text-foreground">Profil</h2>
                  <p className="whitespace-pre-line text-sm text-muted-foreground">{data.bio}</p>
                </section>
              ) : null}
              <section className="flex flex-col gap-2">
                <h2 className="text-sm font-semibold text-foreground">Expériences</h2>
                {data.experiences.length === 0 ? (
                  <p className="text-xs text-muted-foreground">
                    Aucune expérience :{" "}
                    <Link to="/marketplace/profile" className="underline">
                      ajoutez-en depuis votre profil
                    </Link>
                    .
                  </p>
                ) : (
                  data.experiences.map((experience) => (
                    <div key={experience.id} className="flex flex-col border-l-2 border-border pl-3">
                      <span className="text-sm font-medium text-foreground">
                        {experience.title}, {experience.company_name}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(experience.start_date)} –{" "}
                        {experience.is_current || !experience.end_date
                          ? "aujourd'hui"
                          : formatDate(experience.end_date)}
                      </span>
                    </div>
                  ))
                )}
              </section>
              <section className="flex flex-col gap-2">
                <h2 className="text-sm font-semibold text-foreground">Compétences</h2>
                <div className="flex flex-wrap gap-1.5">
                  {data.skills_detail.length === 0 ? (
                    <span className="text-xs text-muted-foreground">Aucune compétence renseignée.</span>
                  ) : (
                    data.skills_detail.map((skill) => (
                      <Badge key={skill.name} variant="outline">
                        {skill.name}
                      </Badge>
                    ))
                  )}
                </div>
              </section>
              {data.rating_avg !== null ? (
                <section className="flex flex-col gap-1">
                  <h2 className="text-sm font-semibold text-foreground">Réputation</h2>
                  <p className="text-sm text-muted-foreground">
                    Note moyenne {data.rating_avg} / 5 sur {data.reviews_count} avis publics
                  </p>
                </section>
              ) : null}
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Mon CV automatique</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-xs leading-relaxed text-muted-foreground">
            Construit depuis votre profil, vos compétences, vos expériences et vos avis publics. Il
            est régénéré à chaque téléchargement, donc toujours à jour.
          </p>
          <div className="flex flex-col gap-2">
            <Label htmlFor="cv-visibility">Visible par</Label>
            <Select
              value={profil?.cv_visibility}
              onValueChange={changeVisibility}
              disabled={isSaving}
            >
              <SelectTrigger id="cv-visibility">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CV_VISIBILITIES.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button type="button" disabled={downloading} onClick={download}>
            <Download className="size-4" />
            Télécharger mon CV (PDF)
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

/** Mon CV : aperçu du CV automatique, visibilité et téléchargement en PDF. */
export default function MyCvPage() {
  return (
    <RequireProfil>
      <MyCvContent />
    </RequireProfil>
  );
}
