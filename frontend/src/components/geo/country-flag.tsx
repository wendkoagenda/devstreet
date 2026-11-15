import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { flagLoader } from "./flags";

const loaded = new Map<string, string>();

export function CountryFlag({
  code,
  className,
}: {
  code: string | null | undefined;
  className?: string;
}) {
  const upper = (code ?? "").toUpperCase();
  const [url, setUrl] = useState<string | null>(() => loaded.get(upper) ?? null);

  useEffect(() => {
    if (!upper) {
      setUrl(null);
      return;
    }
    const cached = loaded.get(upper);
    if (cached) {
      setUrl(cached);
      return;
    }
    const load = flagLoader(upper);
    if (!load) {
      setUrl(null);
      return;
    }
    let active = true;
    load()
      .then((src) => {
        loaded.set(upper, src);
        if (active) setUrl(src);
      })
      .catch((error: unknown) => {
        console.warn(`Drapeau ${upper} indisponible`, error);
      });
    return () => {
      active = false;
    };
  }, [upper]);

  return (
    <span
      aria-hidden
      className={cn(
        "inline-block h-3.5 w-5 shrink-0 overflow-hidden rounded-[3px] bg-muted shadow-[0_0_0_1px_hsl(var(--border))]",
        className
      )}
    >
      {url ? <img src={url} alt="" className="h-full w-full object-cover" loading="lazy" /> : null}
    </span>
  );
}
