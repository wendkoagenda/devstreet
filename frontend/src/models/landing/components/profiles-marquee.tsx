import { useState, type CSSProperties, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { CountryFlag } from "@/components/geo/country-flag";
import { cn } from "@/lib/utils";
import {
  COMPANY_PROFILES,
  DEV_PROFILES,
  type CompanyProfile,
  type DevProfile,
  type DevStatus,
} from "../data/showcase-profiles";

const STATUS_DOT: Record<DevStatus, string> = {
  available: "bg-success",
  mission: "bg-warning",
  open: "bg-info",
};

const COMPANY_TILES = [
  "bg-brand-soft text-brand",
  "bg-success/10 text-success",
  "bg-info/10 text-info",
  "bg-warning/15 text-warning",
];

const CARD_CLASS =
  "w-[18rem] shrink-0 rounded-3xl border border-border/60 bg-card p-4 transition-[transform,box-shadow] duration-300 hover:-translate-y-0.5 hover:shadow-card-hover";

type ShowcaseItem =
  | { kind: "dev"; profile: DevProfile }
  | { kind: "company"; profile: CompanyProfile; index: number };

/** Entreprises réparties régulièrement entre les développeurs, pour mêler les deux publics sur une rangée. */
function buildShowcase(): ShowcaseItem[] {
  const items: ShowcaseItem[] = [];
  let companyCursor = 0;
  DEV_PROFILES.forEach((profile, i) => {
    items.push({ kind: "dev", profile });
    const target = Math.round(((i + 1) * COMPANY_PROFILES.length) / DEV_PROFILES.length);
    for (; companyCursor < target; companyCursor++) {
      items.push({ kind: "company", profile: COMPANY_PROFILES[companyCursor], index: companyCursor });
    }
  });
  return items;
}

const SHOWCASE_ITEMS = buildShowcase();

export function ProfilesMarquee() {
  const { t } = useTranslation();

  return (
    <section aria-labelledby="profils-vitrine">
      <MarqueeRow duration="120s" label={t("landing.profiles.intro")}>
        {SHOWCASE_ITEMS.map((item) =>
          item.kind === "dev" ? (
            <DevCard key={item.profile.id} profile={item.profile} />
          ) : (
            <CompanyCard
              key={item.profile.id}
              profile={item.profile}
              tileClass={COMPANY_TILES[item.index % COMPANY_TILES.length]}
            />
          )
        )}
      </MarqueeRow>

      <p
        id="profils-vitrine"
        className="mx-auto mt-2 max-w-6xl px-4 text-center text-xs text-muted-foreground/80 sm:px-6"
      >
        {t("landing.profiles.intro")} · {t("landing.profiles.note")}
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
    <div className="group relative overflow-hidden py-3 [mask-image:linear-gradient(to_right,transparent,black_8%,black_92%,transparent)] motion-reduce:overflow-x-auto">
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
  const { t } = useTranslation();

  return (
    <li className={CARD_CLASS}>
      <div className="flex items-center gap-3.5">
        <div className="relative shrink-0">
          <Portrait src={profile.photo} initials={profile.initials} />
          <span
            title={t(`landing.profiles.status.${profile.status}`)}
            className={cn(
              "absolute -bottom-0.5 -right-0.5 size-3.5 rounded-full ring-[3px] ring-card",
              STATUS_DOT[profile.status]
            )}
          />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold">{profile.name}</p>
          <p className="truncate text-sm text-muted-foreground">
            {profile.role} · {t("landing.profiles.years", { count: profile.years })}
          </p>
          <Location city={profile.city} country={profile.country} />
        </div>
      </div>
      <TagList tags={profile.stack.slice(0, 2)} />
    </li>
  );
}

function CompanyCard({ profile, tileClass }: { profile: CompanyProfile; tileClass: string }) {
  const { t } = useTranslation();

  return (
    <li className={CARD_CLASS}>
      <div className="flex items-center gap-3.5">
        <span
          className={cn(
            "flex size-14 shrink-0 items-center justify-center rounded-2xl text-base font-bold",
            tileClass
          )}
        >
          {profile.initials}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold">{profile.name}</p>
          <p className="truncate text-sm text-muted-foreground">
            {t(`landing.profiles.sectors.${profile.sector}`)} ·{" "}
            {t("landing.profiles.open_roles", { count: profile.openRoles })}
          </p>
          <Location city={profile.city} country={profile.country} />
        </div>
      </div>
      <TagList tags={profile.seeking.slice(0, 2)} label={t("landing.profiles.seeking")} />
    </li>
  );
}

function Portrait({ src, initials }: { src: string; initials: string }) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <span className="flex size-14 items-center justify-center rounded-2xl bg-brand-soft text-base font-semibold text-brand">
        {initials}
      </span>
    );
  }

  return (
    <img
      src={src}
      alt=""
      width={56}
      height={56}
      decoding="async"
      onError={() => setFailed(true)}
      className="size-14 rounded-2xl bg-muted object-cover"
    />
  );
}

function TagList({ tags, label }: { tags: string[]; label?: string }) {
  return (
    <div className="mt-3.5 flex min-w-0 items-center gap-1.5 overflow-hidden">
      {label ? (
        <span className="shrink-0 text-[11px] text-muted-foreground">{label}</span>
      ) : null}
      {tags.map((tag) => (
        <span
          key={tag}
          className="shrink-0 rounded-full bg-muted px-2.5 py-0.5 text-[11px] font-medium text-muted-foreground"
        >
          {tag}
        </span>
      ))}
    </div>
  );
}

function Location({ city, country }: { city: string; country: string }) {
  return (
    <span className="mt-0.5 flex min-w-0 items-center gap-1.5 text-xs text-muted-foreground">
      <CountryFlag code={country} className="h-3 w-[1.125rem]" />
      <span className="truncate">{city}</span>
    </span>
  );
}
