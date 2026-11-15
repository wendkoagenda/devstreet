import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Users } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Espace } from "../schema";
import { ForumAvatar } from "./forum-avatar";

type EspaceListItemProps = {
  espace: Espace;
  href: string;
};

export function EspaceListItem({ espace, href }: EspaceListItemProps) {
  const { t } = useTranslation();
  const unread = Boolean(espace.has_unread);
  const roleLabel = (() => {
    if (!espace.mon_role) return null;
    if (espace.mon_role === "SUPER_ADMIN") return "Super admin";
    if (espace.mon_role === "ADMIN") return "Admin";
    return espace.type === "CHAINE"
      ? t("forum.action_joined_subscriber")
      : t("forum.action_joined_member");
  })();
  const count = espace.membres_count ?? 0;
  const countLabel =
    espace.type === "CHAINE"
      ? `${count} abonné${count > 1 ? "s" : ""}`
      : `${count} membre${count > 1 ? "s" : ""}`;
  const role = roleLabel;
  const description = espace.description?.trim() ?? "";

  return (
    <Link
      to={href}
      className={cn(
        "relative flex flex-col rounded-xl border bg-card p-3 shadow-sm transition-colors hover:bg-muted/30 hover:shadow-md",
        unread ? "border-brand/40" : "border-border"
      )}
      aria-label={
        unread
          ? t("forum.unread_aria", { name: espace.nom })
          : undefined
      }
    >
      {unread ? (
        <span
          className="absolute right-3 top-3 size-2 rounded-full bg-brand"
          aria-hidden
        />
      ) : null}
      <div className="flex items-start gap-2.5">
        <span className="relative shrink-0">
          <ForumAvatar
            name={espace.nom}
            photo={espace.photo}
            size="md"
            tone="soft"
            className="sm:h-10 sm:w-10 sm:text-sm"
          />
          {unread ? (
            <span
              className="absolute right-0 top-0 size-2.5 rounded-full bg-brand ring-2 ring-card"
              aria-hidden
            />
          ) : null}
        </span>
        <div className="min-w-0 flex-1">
          <h2
            className={cn(
              "truncate text-sm leading-snug text-foreground",
              unread ? "font-bold" : "font-semibold"
            )}
          >
            {espace.nom}
          </h2>
          <p className="mt-0.5 truncate text-xs text-muted-foreground">
            {espace.acces === "LIEN" ? "Accès par lien" : "Public"}
            {role ? <span className="text-brand"> · {role}</span> : null}
            <span className="sm:hidden"> · {countLabel}</span>
          </p>
          {description ? (
            <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
              {description}
            </p>
          ) : null}
        </div>
      </div>

      <div className="mt-2.5 hidden items-center gap-1.5 border-t border-border pt-2 text-xs text-muted-foreground sm:flex">
        <Users className="h-3.5 w-3.5" aria-hidden />
        <span>{countLabel}</span>
        {unread ? (
          <span className="ml-auto font-medium text-brand">
            {t("forum.unread_new")}
          </span>
        ) : null}
      </div>
    </Link>
  );
}
