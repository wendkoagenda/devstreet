import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { useGetMySkillsQuery, useGetSkillOptionsQuery, useSetMySkillsMutation } from "../api";
import type { MySkill } from "../schema";
import { SkillPicker } from "./skill-picker";

const LEVELS = [
  { value: "1", label: "Notions" },
  { value: "2", label: "Débutant" },
  { value: "3", label: "Intermédiaire" },
  { value: "4", label: "Avancé" },
  { value: "5", label: "Expert" },
];

type Row = { skill_id: number; name: string; level: number; years: number };

function SkillsEditor({ initial }: { initial: MySkill[] }) {
  const { t } = useTranslation();
  const { data: options } = useGetSkillOptionsQuery();
  const [save, { isLoading }] = useSetMySkillsMutation();
  const [rows, setRows] = useState<Row[]>(initial);

  const nameOf = (id: number) => options?.find((skill) => skill.id === id)?.name ?? `#${id}`;

  const setIds = (ids: number[]) =>
    setRows(
      ids.map(
        (id) =>
          rows.find((row) => row.skill_id === id) ?? {
            skill_id: id,
            name: nameOf(id),
            level: 3,
            years: 0,
          }
      )
    );

  const patch = (id: number, change: Partial<Row>) =>
    setRows(rows.map((row) => (row.skill_id === id ? { ...row, ...change } : row)));

  const submit = async () => {
    try {
      await save(rows.map(({ skill_id, level, years }) => ({ skill_id, level, years }))).unwrap();
      CreationSuccessSonner("Compétences enregistrées");
    } catch {
      CreationErrorSonner("Impossible d'enregistrer les compétences");
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <SkillPicker value={rows.map((row) => row.skill_id)} onChange={setIds} />

      {rows.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {rows.map((row) => (
            <li
              key={row.skill_id}
              className="flex flex-wrap items-center gap-3 rounded-lg border border-border p-3"
            >
              <span className="min-w-32 flex-1 text-sm font-medium text-foreground">
                {row.name}
              </span>
              <Select
                value={String(row.level)}
                onValueChange={(value) => patch(row.skill_id, { level: Number(value) })}
              >
                <SelectTrigger className="w-40" aria-label={`Niveau en ${row.name}`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LEVELS.map((level) => (
                    <SelectItem key={level.value} value={level.value}>
                      {level.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                type="number"
                min={0}
                max={60}
                className="w-24"
                value={row.years}
                aria-label={`Années de pratique en ${row.name}`}
                onChange={(event) =>
                  patch(row.skill_id, {
                    years: Math.max(0, Math.min(60, Number(event.target.value) || 0)),
                  })
                }
              />
              <span className="text-xs text-muted-foreground">
                {t("marketplace.years_unit_short")}
              </span>
              <Button
                type="button"
                size="icon"
                variant="ghost"
                aria-label={`Retirer ${row.name}`}
                onClick={() => setIds(rows.filter((item) => item.skill_id !== row.skill_id).map((item) => item.skill_id))}
              >
                <X className="size-4" />
              </Button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted-foreground">
          Aucune compétence pour l'instant : elles servent à vous recommander des offres.
        </p>
      )}

      <div className="flex justify-end">
        <Button type="button" disabled={isLoading} onClick={submit}>
          Enregistrer mes compétences
        </Button>
      </div>
    </div>
  );
}

/** Compétences du profil : choix dans le référentiel, niveau et années de pratique. */
export function SkillsCard({ className }: { className?: string }) {
  const { data, isLoading } = useGetMySkillsQuery();

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="size-4" />
          Mes compétences
        </CardTitle>
        <CardDescription>
          Le niveau pèse dans le score de recommandation des offres.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading || !data ? <Skeleton className="h-24 w-full" /> : <SkillsEditor initial={data} />}
      </CardContent>
    </Card>
  );
}
