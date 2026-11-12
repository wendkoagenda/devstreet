/**
 * Variables d'environnement du build (VITE_*) lues SANS valeur de repli :
 * une variable obligatoire absente arrête l'application avec un message qui la nomme.
 */
export const requireEnv = (name: string, value: string | undefined): string => {
  if (value === undefined || value.trim() === "") {
    throw new Error(
      `${name} est obligatoire : définissez-la dans frontend/.env (voir frontend/.env.example).`
    );
  }
  return value;
};
