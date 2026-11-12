import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  BookOpen,
  Globe,
  Lock,
  Search,
  Trash2,
  UserPlus,
  Users,
} from "lucide-react";
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

function MemberAvatar({ userId, label }: { userId: number; label: string }) {
  return (
    <span
      className={cn(
        "inline-flex size-8 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold",
        avatarTone(userId)
      )}
      aria-hidden
    >
      {label}
    </span>
  );
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
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState<"maintainer" | "contributor">("contributor");

  const memberCount = members?.count ?? 0;
  const pageCount = pageCountOf(memberCount, PAGE_SIZE);
  const directAccessCount = memberCount + 1;

  const filteredMembers = useMemo(() => {
    const rows = members?.results ?? [];
    const needle = query.trim().toLowerCase();
    if (!needle) return rows;
    return rows.filter((member) => {
      const label = t("hub.detail.team.user", { id: member.user_id }).toLowerCase();
      const roleLabel = t(`hub.detail.team.roles.${member.role}`).toLowerCase();
      return (
        String(member.user_id).includes(needle) ||
        label.includes(needle) ||
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
    const id = Number(userId);
    if (!Number.isFinite(id) || id <= 0) return;
    const ok = await onInvite({ user_id: id, role });
    if (ok) {
      setUserId("");
      setRole("contributor");
      setInviteOpen(false);
    }
  };

  return (
    <section className="flex flex-col gap-5">
      <div>
        <h2 className="text-xl font-semibold tracking-tight text-foreground">
          {t("hub.detail.team.title")}
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {t("hub.detail.team.subtitle")}
        </p>
      </div>

      {/* Bandeau visibilité */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3">
        <div className="flex min-w-0 items-start gap-3">
          {project.status === "published" ? (
            <Globe aria-hidden className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
          ) : (
            <Lock aria-hidden className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
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
      </div>

      {/* Cartes résumé */}
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs font-medium text-muted-foreground">
            {t("hub.detail.team.summary.base_role")}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="inline-flex rounded-full border border-border bg-secondary px-2.5 py-0.5 text-xs font-semibold text-foreground">
              {t("hub.detail.team.roles.owner")}
            </span>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
            {t("hub.detail.team.summary.base_role_hint")}
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs font-medium text-muted-foreground">
            {t("hub.detail.team.summary.direct")}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <Users aria-hidden className="size-4 text-muted-foreground" />
            <p className="text-sm text-foreground">
              {t("hub.detail.team.summary.direct_count", {
                count: directAccessCount,
              })}
            </p>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {t("hub.detail.team.summary.direct_members", { count: memberCount })}
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs font-medium text-muted-foreground">
            {t("hub.detail.team.summary.org")}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <BookOpen aria-hidden className="size-4 text-muted-foreground" />
            <p className="text-sm text-foreground">
              {t("hub.detail.team.summary.org_count")}
            </p>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {t("hub.detail.team.summary.org_hint")}
          </p>
        </div>
      </div>

      {/* Manage access */}
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-base font-semibold text-foreground">
            {t("hub.detail.team.manage_title")}
          </h3>
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

        <p className="text-xs text-muted-foreground">{t("hub.detail.team.hint")}</p>

        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-3 py-2.5">
            <p className="text-xs font-medium text-muted-foreground">
              {t("hub.detail.team.direct_access_tab")}
            </p>
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
          </div>

          {/* Propriétaire */}
          <div className="flex items-center gap-3 border-b border-border px-3 py-3">
            <MemberAvatar
              userId={project.owner_id}
              label={String(project.owner_id).slice(-2)}
            />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">
                {t("hub.detail.team.user", { id: project.owner_id })}
              </p>
              <p className="text-xs text-muted-foreground">
                {t("hub.detail.team.owner_subtitle")}
              </p>
            </div>
            <span className="inline-flex rounded-md border border-border bg-secondary px-2 py-1 text-[11px] font-semibold text-foreground">
              {t("hub.detail.team.role_label", {
                role: t("hub.detail.team.roles.owner"),
              })}
            </span>
          </div>

          {loading ? (
            <p className="px-3 py-8 text-center text-sm text-muted-foreground">
              {t("common.loading")}
            </p>
          ) : filteredMembers.length === 0 ? (
            <p className="px-3 py-10 text-center text-sm text-muted-foreground">
              {memberCount === 0
                ? t("hub.detail.team.empty")
                : t("hub.detail.team.search_empty")}
            </p>
          ) : (
            <ul>
              {filteredMembers.map((member) => (
                <li
                  key={member.id}
                  className="flex items-center gap-3 border-b border-border px-3 py-3 last:border-b-0"
                >
                  <MemberAvatar
                    userId={member.user_id}
                    label={String(member.user_id).slice(-2)}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">
                      {t("hub.detail.team.user", { id: member.user_id })}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {t(`hub.detail.team.roles.${member.role}`)}
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
                      <SelectTrigger className="h-8 w-[150px] rounded-md bg-secondary text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="contributor">
                          {t("hub.detail.team.role_label", {
                            role: t("hub.detail.team.roles.contributor"),
                          })}
                        </SelectItem>
                        <SelectItem value="maintainer">
                          {t("hub.detail.team.role_label", {
                            role: t("hub.detail.team.roles.maintainer"),
                          })}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <span className="inline-flex rounded-md border border-border bg-secondary px-2 py-1 text-[11px] font-semibold text-foreground">
                      {t("hub.detail.team.role_label", {
                        role: t(`hub.detail.team.roles.${member.role}`),
                      })}
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
              ))}
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
      </div>

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
              <Label htmlFor="member-user-id">{t("hub.detail.team.user_id")}</Label>
              <Input
                id="member-user-id"
                type="number"
                min={1}
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                className="h-9 bg-secondary"
                placeholder="42"
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
                  <SelectItem value="contributor">
                    {t("hub.detail.team.roles.contributor")}
                  </SelectItem>
                  <SelectItem value="maintainer">
                    {t("hub.detail.team.roles.maintainer")}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              className="h-9 text-xs"
              onClick={() => setInviteOpen(false)}
            >
              {t("common.cancel")}
            </Button>
            <Button
              type="button"
              disabled={isBusy || !userId}
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
