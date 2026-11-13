import { useTranslation } from "react-i18next";
import { Skeleton } from "@/components/ui/skeleton";

export function CodeRowsSkeleton() {
  return <div className="divide-y divide-border" aria-hidden>{Array.from({ length: 5 }, (_, index) => <div key={index} className="flex items-center gap-3 px-3 py-3"><Skeleton className="size-4 rounded-sm motion-reduce:animate-none" /><Skeleton className="h-3 w-32 motion-reduce:animate-none" /><Skeleton className="ml-auto hidden h-3 w-44 motion-reduce:animate-none sm:block" /></div>)}</div>;
}

export function CodeBrowserSkeleton() {
  const { t } = useTranslation();
  return <div role="status" aria-busy="true" className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_260px]">
    <span className="sr-only">{t("common.loading")}</span>
    <div className="min-w-0 space-y-3" aria-hidden>
      <Skeleton className="h-5 w-52 motion-reduce:animate-none" />
      <Skeleton className="h-10 w-full motion-reduce:animate-none" />
      <div className="flex justify-between"><Skeleton className="h-8 w-28 motion-reduce:animate-none" /><Skeleton className="h-8 w-24 motion-reduce:animate-none" /></div>
      <div className="overflow-hidden rounded-lg border border-border"><Skeleton className="h-10 rounded-none motion-reduce:animate-none" /><CodeRowsSkeleton /></div>
    </div>
    <div className="space-y-5" aria-hidden><Skeleton className="h-5 w-28 motion-reduce:animate-none" /><Skeleton className="h-14 w-full motion-reduce:animate-none" /><Skeleton className="h-5 w-36 motion-reduce:animate-none" /><Skeleton className="h-8 w-full motion-reduce:animate-none" /></div>
  </div>;
}
