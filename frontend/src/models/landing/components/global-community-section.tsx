import { useState } from "react";
import { CountryFlag } from "@/components/geo/country-flag";
import { GLOBE_CONNECTIONS, type GlobeConnection } from "../data/showcase-profiles";
import { WorldGlobe } from "./world-globe";

const REGIONS = ["Afrique", "Europe", "Amériques", "Asie", "Océanie"] as const;

export function GlobalCommunitySection() {
  const [connection, setConnection] = useState<GlobeConnection>(GLOBE_CONNECTIONS[0]);

  return (
    <section id="monde" className="scroll-mt-24 px-4 pb-16 sm:px-6 sm:pb-24">
      <div className="relative mx-auto grid max-w-6xl items-center gap-8 overflow-hidden rounded-[2rem] border border-border/70 bg-card p-8 shadow-[0_12px_40px_hsl(var(--foreground)/0.08)] sm:p-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] lg:gap-4 lg:p-12">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,hsl(var(--foreground)/0.035)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--foreground)/0.035)_1px,transparent_1px)] bg-[size:28px_28px]"
        />

        <div className="relative">
          <p className="inline-flex w-fit rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
            Partout dans le monde
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl sm:leading-tight">
            Une seule rue, des builders sur tous les fuseaux.
          </h2>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground sm:text-base">
            Des développeurs à Lagos, Bogotá ou Osaka, des équipes à Lisbonne,
            Kigali ou Montréal : les profils se rencontrent sur la stack, pas sur
            la géographie.
          </p>

          <ul className="mt-6 flex flex-wrap gap-2">
            {REGIONS.map((region) => (
              <li
                key={region}
                className="rounded-full border border-border/70 bg-background/60 px-3 py-1 text-xs font-medium text-muted-foreground"
              >
                {region}
              </li>
            ))}
          </ul>

          <ActivityCard connection={connection} />

          <ul className="mt-6 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <li className="inline-flex items-center gap-2">
              <span className="size-2 rounded-full bg-brand" />
              Développeurs
            </li>
            <li className="inline-flex items-center gap-2">
              <span className="size-2 rounded-full bg-success" />
              Entreprises
            </li>
            <li className="inline-flex items-center gap-2">
              <span className="h-0.5 w-5 rounded-full bg-gradient-to-r from-brand to-success" />
              Connexions
            </li>
          </ul>
        </div>

        <div className="relative">
          <div className="relative mx-auto aspect-square w-full max-w-[34rem]">
            <WorldGlobe onConnection={setConnection} />
          </div>
          <p className="mt-1 text-center text-xs text-muted-foreground/80">
            Faites glisser pour faire tourner le globe · activité illustrative
          </p>
        </div>
      </div>
    </section>
  );
}

function ActivityCard({ connection }: { connection: GlobeConnection }) {
  const { dev, company, event } = connection;

  return (
    <div
      aria-live="polite"
      className="mt-8 max-w-md rounded-2xl border border-border/70 bg-background/80 p-4 shadow-card backdrop-blur-sm"
    >
      <div
        key={connection.id}
        className="animate-in fade-in slide-in-from-bottom-1 duration-500 motion-reduce:animate-none"
      >
        <div className="flex items-center justify-between gap-3">
          <span className="rounded-full bg-brand-soft px-2.5 py-0.5 text-xs font-semibold text-brand">
            {event}
          </span>
          <span className="inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span className="size-1.5 rounded-full bg-success" />
            Activité de la rue
          </span>
        </div>
        <div className="mt-3 grid grid-cols-[auto_1fr] items-center gap-x-3 gap-y-2 text-sm">
          <CountryFlag code={dev.country} />
          <p className="min-w-0 truncate">
            <span className="font-medium">
              {dev.role} · {dev.stack[0]}
            </span>
            <span className="text-muted-foreground"> — {dev.city}</span>
          </p>
          <CountryFlag code={company.country} />
          <p className="min-w-0 truncate">
            <span className="font-medium">{company.name}</span>
            <span className="text-muted-foreground"> — {company.city}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
