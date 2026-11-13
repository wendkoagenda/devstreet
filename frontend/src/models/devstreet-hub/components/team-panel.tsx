import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Globe, Lock, Search, Trash2, UserPlus, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { pageCountOf, PAGE_SIZE } from "@/helpers/api/pagination";
import type { Paginated } from "@/helpers/api/pagination";
import { cn } from "@/lib/utils";
import type { Project, ProjectMember, ProjectMemberWrite } from "../schema";

interface TeamPanelProps {
  project: Project;
  members: Paginated<ProjectMember> | undefined;
  loading: boolean;
  page: number;
  onPageChange: (page: number) => void;
  canManage: boolean;
  isBusy: boolean;
  onInvite: (body: ProjectMemberWrite) => Promise<boolean>;
  onUpdateRole: (body: ProjectMemberWrite) => Promise<boolean>;
  onRemove: (userId: number) => void;
}

function avatarTone(userId: number): string {
  const tones = [
    "bg-brand/15 text-brand",
    "bg-success/15 text-success",
    "bg-warning-soft text-foreground",
    "bg-secondary text-muted-foreground",
  ];
  return tones[Math.abs(userId) % tones.length];
}

function initialsOf(label: string): string {
  const parts = label.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
  }
  return label.slice(0, 2).toUpperCase() || "?";
}

function MemberAvatar({ userId, label }: { userId: number; label: string }) {
  return (
    <span
      className={cn(
        "inline-flex size-8 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold",
        avatarTone(userId)
      )}
      aria-hidden
    >
      {initialsOf(label)}
    </span>
  );
}

function memberLabel(
  member: ProjectMember,
  fallback: (id: number) => string
): string {
  return member.display_name || member.username || fallback(member.user_id);
}

export function TeamPanel({
  project,
  members,
  loading,
  page,
  onPageChange,
  canManage,
  isBusy,
  onInvite,
  onUpdateRole,
  onRemove,
}: TeamPanelProps) {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [inviteOpen, setInviteOpen] = useState(false);
  const [identifier, setIdentifier] = useState("");
  const [role, setRole] = useState<"maintainer" | "contributor">("maintainer");

  const memberCount = members?.count ?? 0;
  const pageCount = pageCountOf(memberCount, PAGE_SIZE);
  const ownerLabel =
    project.owner_display_name?.trim() ||
    t("hub.detail.team.user", { id: project.owner_id });

  const filteredMembers = useMemo(() => {
    const rows = members?.results ?? [];
    const needle = query.trim().toLowerCase();
    if (!needle) return rows;
    return rows.filter((member) => {
      const label = memberLabel(member, (id) =>
        t("hub.detail.team.user", { id })
      ).toLowerCase();
      const roleLabel = t(`hub.detail.team.roles.${member.role}`).toLowerCase();
      return (
        String(member.user_id).includes(needle) ||
        label.includes(needle) ||
        (member.username ?? "").toLowerCase().includes(needle) ||
        roleLabel.includes(needle)
      );
    });
  }, [members?.results, query, t]);

  const visibilityKey =
    project.status === "published"
      ? "public"
      : project.status === "archived"
        ? "archived"
        : "draft";

  const handleInvite = async () => {
    const value = identifier.trim();
    if (!value) return;
    const ok = await onInvite({ identifier: value, role });
    if (ok) {
      setIdentifier("");
      setRole("maintainer");
      setInviteOpen(false);
    }
  };

  return (
    <section className="flex flex-col gap-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-foreground">
            {t("hub.detail.team.title")}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {t("hub.detail.team.subtitle")}
          </p>
        </div>
        {canManage ? (
          <Button
            type="button"
            variant="outline"
            className="h-8 gap-1.5 rounded-md text-xs font-medium"
            onClick={() => setInviteOpen(true)}
          >
            <UserPlus aria-hidden className="size-3.5" />
            {t("hub.detail.team.add_people")}
          </Button>
        ) : null}
      </div>

      <div className="flex flex-wrap items-start gap-3 rounded-lg border border-border bg-card px-4 py-3">
        {project.status === "published" ? (
          <Globe
            aria-hidden
            className="mt-0.5 size-4 shrink-0 text-muted-foreground"
          />
        ) : (
          <Lock
            aria-hidden
            className="mt-0.5 size-4 shrink-0 text-muted-foreground"
          />
        )}
        <div className="min-w-0">
          <p className="text-sm font-medium text-foreground">
            {t(`hub.detail.team.visibility.${visibilityKey}.title`)}
          </p>
          <p className="text-xs text-muted-foreground">
            {t(`hub.detail.team.visibility.${visibilityKey}.hint`)}
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-lg border border-border bg-card">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-3 py-2.5">
          <p className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <Users aria-hidden className="size-3.5" />
            {t("hub.detail.team.list_title")}
          </p>
          {memberCount > 0 ? (
            <div className="relative w-full max-w-xs">
              <Search
                aria-hidden
                className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground"
              />
              <Input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder={t("hub.detail.team.search_placeholder")}
                className="h-8 rounded-md bg-secondary pl-8 text-xs"
              />
            </div>
          ) : null}
        </div>

        <div className="flex items-center gap-3 border-b border-border px-3 py-3">
          <MemberAvatar userId={project.owner_id} label={ownerLabel} />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-foreground">
              {ownerLabel}
            </p>
            <p className="text-xs text-muted-foreground">
              {t("hub.detail.team.owner_subtitle")}
            </p>
          </div>
          <span className="inline-flex rounded-md border border-border bg-secondary px-2 py-1 text-[11px] font-semibold text-foreground">
            {t("hub.detail.team.roles.owner")}
          </span>
        </div>

        {loading ? (
          <p className="px-3 py-8 text-center text-sm text-muted-foreground">
            {t("common.loading")}
          </p>
        ) : memberCount === 0 ? (
          <div className="flex flex-col items-center gap-3 px-4 py-10 text-center">
            <p className="max-w-sm text-sm text-muted-foreground">
              {t("hub.detail.team.empty")}
            </p>
            {canManage ? (
              <Button
                type="button"
                variant="outline"
                className="h-8 gap-1.5 rounded-md text-xs font-medium"
                onClick={() => setInviteOpen(true)}
              >
                <UserPlus aria-hidden className="size-3.5" />
                {t("hub.detail.team.add_people")}
              </Button>
            ) : null}
          </div>
        ) : filteredMembers.length === 0 ? (
          <p className="px-3 py-10 text-center text-sm text-muted-foreground">
            {t("hub.detail.team.search_empty")}
          </p>
        ) : (
          <ul>
            {filteredMembers.map((member) => {
              const label = memberLabel(member, (id) =>
                t("hub.detail.team.user", { id })
              );
              return (
                <li
                  key={member.id}
                  className="flex items-center gap-3 border-b border-border px-3 py-3 last:border-b-0"
                >
                  <MemberAvatar userId={member.user_id} label={label} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">
                      {label}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {t(`hub.detail.team.role_hints.${member.role}`)}
                    </p>
                  </div>

                  {canManage ? (
                    <Select
                      value={member.role}
                      disabled={isBusy}
                      onValueChange={(value) => {
                        void onUpdateRole({
                          user_id: member.user_id,
                          role: value as "maintainer" | "contributor",
                        });
                      }}
                    >
                      <SelectTrigger className="h-8 w-[200px] rounded-md bg-secondary text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="maintainer">
                          {t("hub.detail.team.roles.maintainer")}
                        </SelectItem>
                        <SelectItem value="contributor">
                          {t("hub.detail.team.roles.contributor")}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <span className="inline-flex rounded-md border border-border bg-secondary px-2 py-1 text-[11px] font-semibold text-foreground">
                      {t(`hub.detail.team.roles.${member.role}`)}
                    </span>
                  )}

                  {canManage ? (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      disabled={isBusy}
                      className="h-8 w-8 shrink-0 text-destructive hover:bg-destructive/10 hover:text-destructive"
                      aria-label={t("hub.detail.team.remove")}
                      onClick={() => onRemove(member.user_id)}
                    >
                      <Trash2 aria-hidden className="size-3.5" />
                    </Button>
                  ) : null}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {pageCount > 1 ? (
        <div className="flex items-center justify-between gap-2 text-xs">
          <Button
            type="button"
            variant="outline"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="h-8 rounded-md"
          >
            {t("pagination.previous")}
          </Button>
          <span className="text-muted-foreground">
            {t("hub.detail.page_of", { page, pageCount })}
          </span>
          <Button
            type="button"
            variant="outline"
            disabled={page >= pageCount}
            onClick={() => onPageChange(page + 1)}
            className="h-8 rounded-md"
          >
            {t("pagination.next")}
          </Button>
        </div>
      ) : null}

      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{t("hub.detail.team.invite_dialog.title")}</DialogTitle>
            <DialogDescription>
              {t("hub.detail.team.invite_dialog.description")}
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3 py-1">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="member-identifier">
                {t("hub.detail.team.identifier")}
              </Label>
              <Input
                id="member-identifier"
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                className="h-9 bg-secondary"
                placeholder={t("hub.detail.team.identifier_placeholder")}
                autoComplete="off"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label>{t("hub.detail.team.role")}</Label>
              <Select
                value={role}
                onValueChange={(value) =>
                  setRole(value as "maintainer" | "contributor")
                }
              >
                <SelectTrigger className="h-9 rounded-md bg-secondary text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="maintainer">
                    {t("hub.detail.team.roles.maintainer")}
                  </SelectItem>
                  <SelectItem value="contributor">
                    {t("hub.detail.team.roles.contributor")}
                  </SelectItem>
                </SelectContent>
              </Select>
              <p className="text-[11px] text-muted-foreground">
                {t(`hub.detail.team.role_hints.${role}`)}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              className="h-9 text-xs"
              onClick={() => setInviteOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              disabled={isBusy || !identifier.trim()}
              className="h-9 text-xs font-semibold"
              onClick={() => void handleInvite()}
            >
              {t("hub.detail.team.invite")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
