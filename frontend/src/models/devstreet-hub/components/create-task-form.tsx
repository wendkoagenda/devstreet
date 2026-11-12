import {
  Bold,
  Code2,
  Heading1,
  Heading2,
  Heading3,
  Italic,
  Link2,
  List,
  ListOrdered,
  ListTodo,
  Quote,
  Strikethrough,
} from "lucide-react";
import { useRef, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { SafeMarkdown } from "../functions/safe-markdown";
import type { TaskWrite } from "../schema";

interface CreateTaskFormProps {
  isBusy: boolean;
  onSubmit: (body: TaskWrite) => Promise<boolean>;
  onCancel: () => void;
}

type EditorMode = "write" | "preview";

function insertAround(
  textarea: HTMLTextAreaElement,
  before: string,
  after = "",
  placeholder = ""
): string {
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const value = textarea.value;
  const selected = value.slice(start, end) || placeholder;
  const next = value.slice(0, start) + before + selected + after + value.slice(end);
  const cursor = start + before.length + selected.length;
  requestAnimationFrame(() => {
    textarea.focus();
    textarea.setSelectionRange(cursor, cursor);
  });
  return next;
}

function insertLinePrefix(textarea: HTMLTextAreaElement, prefix: string): string {
  const start = textarea.selectionStart;
  const value = textarea.value;
  const lineStart = value.lastIndexOf("\n", start - 1) + 1;
  const next =
    value.slice(0, lineStart) + prefix + value.slice(lineStart);
  const cursor = start + prefix.length;
  requestAnimationFrame(() => {
    textarea.focus();
    textarea.setSelectionRange(cursor, cursor);
  });
  return next;
}

interface ToolButtonProps {
  label: string;
  onClick: () => void;
  children: ReactNode;
}

function ToolButton({ label, onClick, children }: ToolButtonProps) {
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      onClick={onClick}
      className="inline-flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
    >
      {children}
    </button>
  );
}

/**
 * Formulaire « Nouvelle tâche » — structure forge (ticket) : titre, éditeur
 * Écrire/Aperçu + barre Markdown, actions, panneau latéral métadonnées DevStreet.
 */
export function CreateTaskForm({ isBusy, onSubmit, onCancel }: CreateTaskFormProps) {
  const { t } = useTranslation();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [criteriaText, setCriteriaText] = useState("");
  const [mode, setMode] = useState<EditorMode>("write");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const apply = (mutator: (el: HTMLTextAreaElement) => string) => {
    const el = textareaRef.current;
    if (!el) return;
    setDescription(mutator(el));
  };

  const parseCriteria = (): string[] =>
    criteriaText
      .split("\n")
      .map((line) => line.replace(/^[-*]\s*/, "").trim())
      .filter(Boolean)
      .slice(0, 10);

  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={(event) => {
        event.preventDefault();
        const criteria = parseCriteria();
        void onSubmit({
          title: title.trim(),
          description: description.trim(),
          acceptance_criteria: criteria.length ? criteria : undefined,
        }).then((ok) => {
          if (ok) {
            setTitle("");
            setDescription("");
            setCriteriaText("");
            setMode("write");
          }
        });
      }}
    >
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-bold text-foreground">
          {t("hub.detail.task_form.page_title")}
        </h2>
        <Button
          type="button"
          variant="ghost"
          className="h-8 text-xs text-muted-foreground"
          onClick={onCancel}
        >
          {t("common.cancel")}
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[minmax(0,1fr)_260px]">
        <div className="flex min-w-0 flex-col gap-3">
          <Input
            id="task-title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder={t("hub.detail.task_form.name_placeholder")}
            className="h-11 rounded-lg border-border bg-card text-sm font-medium"
            required
            maxLength={180}
            autoFocus
          />

          <div className="overflow-hidden rounded-lg border border-border bg-card">
            <div className="flex items-center gap-0 border-b border-border bg-secondary/40 px-2">
              <button
                type="button"
                onClick={() => setMode("write")}
                className={cn(
                  "relative px-3 py-2 text-xs font-semibold transition-colors",
                  mode === "write"
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {t("hub.detail.task_form.tab_write")}
                {mode === "write" ? (
                  <span className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-brand" />
                ) : null}
              </button>
              <button
                type="button"
                onClick={() => setMode("preview")}
                className={cn(
                  "relative px-3 py-2 text-xs font-semibold transition-colors",
                  mode === "preview"
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {t("hub.detail.task_form.tab_preview")}
                {mode === "preview" ? (
                  <span className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-brand" />
                ) : null}
              </button>
            </div>

            {mode === "write" ? (
              <>
                <div className="flex flex-wrap items-center gap-0.5 border-b border-border px-2 py-1.5">
                  <ToolButton
                    label="H1"
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "# "))
                    }
                  >
                    <Heading1 className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label="H2"
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "## "))
                    }
                  >
                    <Heading2 className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label="H3"
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "### "))
                    }
                  >
                    <Heading3 className="size-3.5" />
                  </ToolButton>
                  <span className="mx-1 h-4 w-px bg-border" />
                  <ToolButton
                    label={t("hub.detail.task_form.tool_bold")}
                    onClick={() =>
                      apply((el) => insertAround(el, "**", "**", "texte"))
                    }
                  >
                    <Bold className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label={t("hub.detail.task_form.tool_italic")}
                    onClick={() =>
                      apply((el) => insertAround(el, "*", "*", "texte"))
                    }
                  >
                    <Italic className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label={t("hub.detail.task_form.tool_strike")}
                    onClick={() =>
                      apply((el) => insertAround(el, "~~", "~~", "texte"))
                    }
                  >
                    <Strikethrough className="size-3.5" />
                  </ToolButton>
                  <span className="mx-1 h-4 w-px bg-border" />
                  <ToolButton
                    label={t("hub.detail.task_form.tool_quote")}
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "> "))
                    }
                  >
                    <Quote className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label={t("hub.detail.task_form.tool_code")}
                    onClick={() =>
                      apply((el) => insertAround(el, "`", "`", "code"))
                    }
                  >
                    <Code2 className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label={t("hub.detail.task_form.tool_link")}
                    onClick={() =>
                      apply((el) =>
                        insertAround(el, "[", "](https://)", "lien")
                      )
                    }
                  >
                    <Link2 className="size-3.5" />
                  </ToolButton>
                  <span className="mx-1 h-4 w-px bg-border" />
                  <ToolButton
                    label={t("hub.detail.task_form.tool_list")}
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "- "))
                    }
                  >
                    <List className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label={t("hub.detail.task_form.tool_ordered")}
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "1. "))
                    }
                  >
                    <ListOrdered className="size-3.5" />
                  </ToolButton>
                  <ToolButton
                    label={t("hub.detail.task_form.tool_checklist")}
                    onClick={() =>
                      apply((el) => insertLinePrefix(el, "- [ ] "))
                    }
                  >
                    <ListTodo className="size-3.5" />
                  </ToolButton>
                </div>
                <Textarea
                  ref={textareaRef}
                  id="task-description"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder={t("hub.detail.task_form.body_placeholder")}
                  className="min-h-[220px] resize-y rounded-none border-0 bg-transparent px-4 py-3 text-sm shadow-none focus-visible:ring-0"
                />
              </>
            ) : (
              <div className="min-h-[280px] px-4 py-3 text-sm">
                {description.trim() ? (
                  <SafeMarkdown content={description} />
                ) : (
                  <p className="text-muted-foreground">
                    {t("hub.detail.task_form.preview_empty")}
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              className="h-9 rounded-lg text-xs"
            >
              {t("common.cancel")}
            </Button>
            <Button
              type="submit"
              disabled={isBusy || !title.trim()}
              className="h-9 rounded-lg text-xs font-semibold"
            >
              {isBusy
                ? t("hub.detail.task_form.submitting")
                : t("hub.detail.task_form.submit")}
            </Button>
          </div>
        </div>

        <aside className="flex flex-col gap-0 overflow-hidden rounded-lg border border-border bg-card text-xs">
          <div className="border-b border-border px-3 py-3">
            <p className="mb-1 font-semibold text-foreground">
              {t("hub.detail.task_form.sidebar_status")}
            </p>
            <p className="text-muted-foreground">
              {t("hub.detail.task_form.sidebar_status_value")}
            </p>
          </div>
          <div className="border-b border-border px-3 py-3">
            <p className="mb-1.5 font-semibold text-foreground">
              {t("hub.detail.task_form.sidebar_criteria")}
            </p>
            <Textarea
              value={criteriaText}
              onChange={(event) => setCriteriaText(event.target.value)}
              placeholder={t("hub.detail.task_form.criteria_placeholder")}
              className="min-h-[100px] rounded-md border-border bg-secondary/50 text-xs"
            />
            <p className="mt-1.5 text-[11px] text-muted-foreground">
              {t("hub.detail.task_form.criteria_hint")}
            </p>
          </div>
          <div className="px-3 py-3">
            <p className="mb-1 font-semibold text-foreground">
              {t("hub.detail.task_form.sidebar_note_title")}
            </p>
            <p className="leading-relaxed text-muted-foreground">
              {t("hub.detail.task_form.sidebar_note_text")}
            </p>
          </div>
        </aside>
      </div>
    </form>
  );
}
