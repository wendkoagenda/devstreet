import { API_V1_URL } from "@/helpers/api/csrf";

/** Nom de fichier proposé par le serveur (« CV_Prenom_Nom.pdf »), avec un repli sûr. */
function filenameOf(response: Response): string {
  const header = response.headers.get("Content-Disposition") ?? "";
  const match = /filename="?([^";]+)"?/i.exec(header);
  return match?.[1] ?? "CV.pdf";
}

/**
 * Télécharge le CV en PDF : celui de l'utilisateur connecté (sans argument) ou celui d'un profil.
 * Le serveur applique la visibilité du CV (public, entreprises, privé) ; lève une erreur s'il refuse.
 */
export async function downloadCv(profilId?: number): Promise<void> {
  const path = profilId ? `/marketplace/profils/${profilId}/cv` : "/marketplace/me/cv";
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
