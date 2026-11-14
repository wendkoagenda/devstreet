import { Link } from "react-router-dom";
import { Users } from "lucide-react";
import type { Espace } from "../schema";
import { ForumAvatar } from "./forum-avatar";

type EspaceListItemProps = {
  espace: Espace;
  href: string;
};

function roleLabel(espace: Espace) {
  if (!espace.mon_role) return null;
  if (espace.mon_role === "SUPER_ADMIN") return "Super admin";
  if (espace.mon_role === "ADMIN") return "Admin";
  return espace.type === "CHAINE" ? "Abonné" : "Membre";
}

export function EspaceListItem({ espace, href }: EspaceListItemProps) {
  const count = espace.membres_count ?? 0;
  const countLabel =
    espace.type === "CHAINE"
      ? `${count} abonné${count > 1 ? "s" : ""}`
      : `${count} membre${count > 1 ? "s" : ""}`;
  const role = roleLabel(espace);
  const description = espace.description?.trim() ?? "";

  return (
    <Link
      to={href}
      className="flex flex-col gap-0 rounded-xl border border-border bg-card p-3 shadow-sm transition-colors hover:bg-muted/30 hover:shadow-md sm:h-full sm:rounded-2xl sm:p-4"
    >
      <div className="flex items-start gap-3">
        <ForumAvatar
          name={espace.nom}
          photo={espace.photo}
          size="md"
          tone="soft"
          className="sm:h-12 sm:w-12 sm:text-sm"
        />
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-sm font-semibold text-foreground sm:line-clamp-2 sm:text-[15px] sm:leading-snug">
            {espace.nom}
          </h2>
          <p className="mt-0.5 truncate text-xs text-muted-foreground sm:mt-1">
            {espace.acces === "LIEN" ? "Accès par lien" : "Public"}
            {role ? <span className="text-brand"> · {role}</span> : null}
            <span className="sm:hidden"> · {countLabel}</span>
          </p>
          {description ? (
            <p className="mt-1 line-clamp-1 text-xs text-muted-foreground sm:hidden">
              {description}
            </p>
          ) : null}
        </div>
      </div>

      <p className="mt-3 hidden line-clamp-3 flex-1 text-sm text-muted-foreground sm:block">
        {description ||
          (espace.type === "CHAINE"
            ? "Aucune description pour cette chaîne."
            : "Aucune description pour cette communauté.")}
      </p>

      <div className="mt-4 hidden items-center gap-1.5 border-t border-border pt-3 text-xs text-muted-foreground sm:flex">
        <Users className="h-3.5 w-3.5" aria-hidden />
        <span>{countLabel}</span>
      </div>
    </Link>
  );
}
