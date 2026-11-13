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

  return (
    <Link
      to={href}
      className="flex h-full flex-col rounded-2xl border border-border bg-card p-4 shadow-sm transition-colors hover:bg-muted/30 hover:shadow-md"
    >
      <div className="flex items-start gap-3">
        <ForumAvatar
          name={espace.nom}
          photo={espace.photo}
          size="lg"
          tone="soft"
        />
        <div className="min-w-0 flex-1">
          <h2 className="line-clamp-2 text-[15px] font-semibold leading-snug text-foreground">
            {espace.nom}
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            {espace.acces === "LIEN" ? "Accès par lien" : "Public"}
            {role ? <span className="text-brand"> · {role}</span> : null}
          </p>
        </div>
      </div>

      <p className="mt-3 line-clamp-3 flex-1 text-sm text-muted-foreground">
        {espace.description?.trim() ||
          (espace.type === "CHAINE"
            ? "Aucune description pour cette chaîne."
            : "Aucune description pour cette communauté.")}
      </p>

      <div className="mt-4 flex items-center gap-1.5 border-t border-border pt-3 text-xs text-muted-foreground">
        <Users className="h-3.5 w-3.5" aria-hidden />
        <span>{countLabel}</span>
      </div>
    </Link>
  );
}
