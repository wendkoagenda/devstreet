import { ReactNode } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";

/**
 * Mise en page commune des pages d'authentification publiques
 * (connexion, mot de passe oublié) : logo, carte centrée, bascules langue/thème.
 */
export default function AuthLayout({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-muted/40 p-4">
      {/* Halo décoratif : suit le thème via les couleurs d'accent */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <div className="absolute -top-32 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-chart-1/10 blur-3xl" />
        <div className="absolute -bottom-32 right-0 h-96 w-96 rounded-full bg-chart-2/10 blur-3xl" />
      </div>

      <div className="absolute right-4 top-4 flex items-center gap-2">
        <LanguageToggle />
        <ModeToggle />
      </div>

      <div className="relative w-full max-w-md space-y-6">
        <div className="flex justify-center">
          {/* Logo bleu : inversé en blanc en mode sombre pour rester lisible */}
          <img
            src="/devstreet-logo.png"
            alt="devstreet"
            className="h-14 w-auto dark:brightness-0 dark:invert"
          />
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-semibold">{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </CardHeader>
          <CardContent>{children}</CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} OnePourcent
        </p>
      </div>
    </div>
  );
}
