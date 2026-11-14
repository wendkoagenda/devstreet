import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Star } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import {
  CheckboxField,
  SelectField,
  TextareaField,
} from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { useCreateReviewMutation, useGetPendingReviewsQuery } from "../api";
import {
  reviewFormSchema,
  type PendingReview,
  type ReviewFormValues,
} from "../schema";

const RATING_OPTIONS = [5, 4, 3, 2, 1].map((value) => ({
  value: String(value),
  label: `${value} / 5`,
}));

function ReviewForm({
  pending,
  onDone,
}: {
  pending: PendingReview;
  onDone: () => void;
}) {
  const { t } = useTranslation();
  const [create, { isLoading }] = useCreateReviewMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);
  const form = useForm<ReviewFormValues>({
    resolver: zodResolver(reviewFormSchema),
    defaultValues: { rating: "5", comment: "", is_public: true },
  });

  const onSubmit = async (values: ReviewFormValues) => {
    setGlobalError(null);
    try {
      await create({
        candidature_id: pending.candidature_id,
        rating: Number(values.rating),
        comment: values.comment,
        is_public: values.is_public,
      }).unwrap();
      CreationSuccessSonner("Avis enregistré");
      onDone();
    } catch (err) {
      setGlobalError(applySubmitError(err, form, t));
    }
  };

  return (
    <Form {...form}>
      <form className="flex flex-col gap-3" noValidate onSubmit={form.handleSubmit(onSubmit)}>
        {globalError}
        <p className="text-sm text-foreground">
          Noter <span className="font-medium">{pending.target.name}</span> pour « {pending.offer.title} »
        </p>
        <SelectField
          control={form.control}
          name="rating"
          label="Note"
          options={RATING_OPTIONS}
        />
        <TextareaField control={form.control} name="comment" label="Commentaire" rows={3} />
        <CheckboxField control={form.control} name="is_public" label="Avis public (profil et CV)" />
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onDone}>
            Annuler
          </Button>
          <Button type="submit" disabled={isLoading}>
            Envoyer l'avis
          </Button>
        </div>
      </form>
    </Form>
  );
}

/** Missions acceptées en attente d'un avis (UC-12). */
export function PendingReviewsCard({ className }: { className?: string }) {
  const { data, isLoading } = useGetPendingReviewsQuery();
  const [editing, setEditing] = useState<PendingReview | null>(null);

  if (!isLoading && (data?.length ?? 0) === 0) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Star className="size-4" />
          À noter
        </CardTitle>
        <CardDescription>Après une mission acceptée, notez l'autre partie.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {isLoading ? <Skeleton className="h-16 w-full" /> : null}
        {editing ? (
          <ReviewForm pending={editing} onDone={() => setEditing(null)} />
        ) : (
          (data ?? []).map((item) => (
            <div
              key={item.candidature_id}
              className="flex items-start justify-between gap-3 rounded-lg border border-border p-3"
            >
              <div className="min-w-0">
                <p className="text-sm font-medium text-foreground">{item.target.name}</p>
                <p className="truncate text-xs text-muted-foreground">{item.offer.title}</p>
              </div>
              <Button type="button" size="sm" onClick={() => setEditing(item)}>
                Noter
              </Button>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
