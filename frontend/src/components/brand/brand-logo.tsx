import { cn } from "@/lib/utils";

const ASSETS = {
  wordmark: {
    onLight: "/devstreet-logo-clair-transparent.svg",
    onDark: "/devstreet-logo-sombre-transparent.svg",
  },
  mark: {
    src: "/devstreet-icone.svg",
  },
} as const;

type BrandLogoProps = {
  /** Mot-symbole complet ou pictogramme seul. */
  variant?: "wordmark" | "mark";
  /**
   * Fond sur lequel le logo est posé.
   * - auto : suit le thème clair/sombre de l'app
   * - light / dark : forcé (ex. panneau coloré)
   */
  on?: "auto" | "light" | "dark";
  alt?: string;
  className?: string;
};

/**
 * Logo DevStreet (assets dans /public).
 * Utilise les variantes transparentes SVG pour rester net à toutes les densités.
 */
export function BrandLogo({
  variant = "wordmark",
  on = "auto",
  alt = "DevStreet",
  className,
}: BrandLogoProps) {
  if (variant === "mark") {
    return (
      <img
        src={ASSETS.mark.src}
        alt={alt}
        className={cn("size-8 object-contain", className)}
        decoding="async"
      />
    );
  }

  const src =
    on === "dark" ? ASSETS.wordmark.onDark : ASSETS.wordmark.onLight;

  if (on !== "auto") {
    return (
      <img
        src={src}
        alt={alt}
        className={cn("h-10 w-auto object-contain object-left", className)}
        decoding="async"
      />
    );
  }

  return (
    <span className={cn("inline-flex h-10 items-center", className)}>
      <img
        src={ASSETS.wordmark.onLight}
        alt={alt}
        className="h-full w-auto object-contain object-left dark:hidden"
        decoding="async"
      />
      <img
        src={ASSETS.wordmark.onDark}
        alt={alt}
        className="hidden h-full w-auto object-contain object-left dark:block"
        decoding="async"
      />
    </span>
  );
}
