import { API_V1_URL } from "@/helpers/api/csrf";
import { previewQuery, type CvSettings } from "./cv-settings";

/** Nom de fichier proposé par le serveur (« CV_Prenom_Nom.pdf »), avec un repli sûr. */
function filenameOf(response: Response): string {
  const header = response.headers.get("Content-Disposition") ?? "";
  const match = /filename="?([^";]+)"?/i.exec(header);
  return match?.[1] ?? "CV.pdf";
}

/**
 * Télécharge le CV en PDF : celui de l'utilisateur connecté (sans argument) ou celui d'un profil.
 * Le serveur applique la visibilité du CV (public, entreprises, privé) ; lève une erreur s'il refuse.
 * `preview` : réglages pas encore enregistrés, appliqués à mon propre CV seulement (ignorés pour un autre profil).
 */
export async function downloadCv(profilId?: number, preview?: CvSettings): Promise<void> {
  const base = profilId ? `/marketplace/profils/${profilId}/cv` : "/marketplace/me/cv";
  const path = !profilId && preview ? `${base}?${previewQuery(preview)}` : base;
  const response = await fetch(`${API_V1_URL}${path}`, { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Téléchargement du CV refusé (${response.status})`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filenameOf(response);
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
