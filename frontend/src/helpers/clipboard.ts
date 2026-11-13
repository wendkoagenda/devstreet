import i18n from "i18next";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";

/**
 * Copie un texte dans le presse-papiers.
 * Un échec (permission refusée, contexte non sécurisé) est journalisé et signalé à l'utilisateur ;
 * le résultat indique si la copie a réussi.
 */
export async function copyText(value: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch (error) {
    console.error("Copie dans le presse-papiers impossible :", error);
    CreationErrorSonner(i18n.t("copy_failed"));
    return false;
  }
}
