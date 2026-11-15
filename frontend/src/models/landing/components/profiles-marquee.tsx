import type { CSSProperties, ReactNode } from "react";
import { CountryFlag } from "@/components/geo/country-flag";
import { cn } from "@/lib/utils";
import {
  COMPANY_PROFILES,
  DEV_PROFILES,
  type CompanyProfile,
  type DevProfile,
  type DevStatus,
} from "../data/showcase-profiles";

const STATUS_LABELS: Record<DevStatus, { label: string; dotClass: string }> = {
  available: { label: "Dispo", dotClass: "bg-success" },
  mission: { label: "En mission", dotClass: "bg-warning" },
  open: { label: "À l'écoute", dotClass: "bg-info" },
};

export function ProfilesMarquee() {
  return (
    <section aria-labelledby="profils-vitrine" className="relative pb-14 pt-4 sm:pb-20">
      <div className="mx-auto max-w-6xl px-4 text-center sm:px-6">
        <p
          id="profils-vitrine"
          className="text-sm font-medium text-muted-foreground sm:text-[0.9375rem]"
        >
          De Dakar à Osaka, des développeurs et des entreprises qui construisent
          ensemble.
        </p>
      </div>

      <div className="mt-8 space-y-4">
        <MarqueeRow duration="80s" label="Profils de développeurs">
          {DEV_PROFILES.map((profile) => (
            <DevCard key={profile.id} profile={profile} />
          ))}
        </MarqueeRow>
        <MarqueeRow duration="95s" label="Profils d'entreprises">
          {COMPANY_PROFILES.map((profile) => (
            <CompanyCard key={profile.id} profile={profile} />
          ))}
        </MarqueeRow>
      </div>

      <p className="mt-6 text-center text-xs text-muted-foreground/80">
        Exemples de profils anonymisés
      </p>
    </section>
  );
}

function MarqueeRow({
  children,
  duration,
  label,
}: {
  children: ReactNode;
  duration: string;
  label: string;
}) {
  return (
    <div className="group relative overflow-hidden py-1 [mask-image:linear-gradient(to_right,transparent,black_7%,black_93%,transparent)] motion-reduce:overflow-x-auto">
      <div
        className="flex w-max animate-marquee-right group-hover:[animation-play-state:paused] motion-reduce:animate-none"
        style={{ "--marquee-duration": duration } as CSSProperties}
      >
        {/* La seconde copie rend la boucle continue : translateX(-50%) retombe exactement sur la première. */}
        {[0, 1].map((copy) => (
          <ul
            key={copy}
            aria-label={copy === 0 ? label : undefined}
            aria-hidden={copy === 1 || undefined}
            className="flex shrink-0 gap-4 pr-4"
          >
            {children}
          </ul>
        ))}
      </div>
    </div>
  );
}

function DevCard({ profile }: { profile: DevProfile }) {
  const status = STATUS_LABELS[profile.status];

  return (
    <li className="w-[17.5rem] shrink-0 rounded-2xl border border-border/70 bg-card p-4 shadow-card transition-shadow hover:shadow-card-hover">
      <div className="flex items-start gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand-soft text-sm font-semibold text-brand">
          {profile.initials}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold">{profile.name}</p>
          <p className="truncate text-xs text-muted-foreground">
            {profile.role}
          </p>
        </div>
        <span className="inline-flex shrink-0 items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
          <span className={cn("size-1.5 rounded-full", status.dotClass)} />
          {status.label}
        </span>
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        <TagList tags={profile.stack} />
        <Location city={profile.city} country={profile.country} />
      </div>
    </li>
  );
}

function CompanyCard({ profile }: { profile: CompanyProfile }) {
  return (
    <li className="w-[17.5rem] shrink-0 rounded-2xl border border-border/70 bg-card p-4 shadow-card transition-shadow hover:shadow-card-hover">
      <div className="flex items-start gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-success/10 text-sm font-semibold text-success">
          {profile.initials}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold">{profile.name}</p>
          <p className="truncate text-xs text-muted-foreground">
            {profile.sector} · {profile.size}
          </p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-1.5">
          <span className="shrink-0 text-[11px] text-muted-foreground">
            Cherche
          </span>
          <TagList tags={profile.seeking} />
        </div>
        <Location city={profile.city} country={profile.country} />
      </div>
    </li>
  );
}

function TagList({ tags }: { tags: string[] }) {
  return (
    <div className="flex min-w-0 gap-1.5 overflow-hidden">
      {tags.map((tag) => (
        <span
          key={tag}
          className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground"
        >
          {tag}
        </span>
      ))}
    </div>
  );
}

function Location({ city, country }: { city: string; country: string }) {
  return (
    <span className="inline-flex min-w-0 shrink items-center gap-1.5 text-[11px] text-muted-foreground">
      <CountryFlag code={country} className="h-3 w-[1.125rem]" />
      <span className="truncate">{city}</span>
    </span>
  );
}
