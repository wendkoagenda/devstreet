import { Skeleton } from "@/components/ui/skeleton";

export default function UserTableLoader() {
  return (
    <div className="w-full animate-pulse">
      
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-[220px]" />
          <Skeleton className="h-10 w-[180px]" />
          <Skeleton className="h-10 w-[150px]" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-[100px]" />
          <Skeleton className="h-10 w-[120px]" />
        </div>
      </div>

     
      <div className="rounded-md border overflow-hidden">
        <div className="grid grid-cols-12 gap-4 p-4 border-b">
          {[...Array(6)].map((_, i) => (
            <Skeleton 
              key={i} 
              className={`h-6 ${i === 5 ? 'col-span-2' : 'col-span-2'}`} 
            />
          ))}
        </div>

       
        <div className="space-y-4 p-4">
          {[...Array(3)].map((_, rowIndex) => (
            <div 
              key={rowIndex} 
              className="grid grid-cols-12 gap-4 py-3"
            >
              {[...Array(6)].map((_, colIndex) => (
                <div 
                  key={colIndex} 
                  className={`${colIndex === 5 ? 'col-span-2 flex justify-end gap-2' : 'col-span-2'}`}
                >
                  {colIndex === 5 ? (
                    <>
                      <Skeleton className="h-8 w-8 rounded-md" />
                      <Skeleton className="h-8 w-8 rounded-md" />
                    </>
                  ) : (
                    <Skeleton className="h-5" />
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1">
          <Skeleton className="h-5 w-[200px]" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-9 w-24 rounded-md" />
          <Skeleton className="h-9 w-24 rounded-md" />
        </div>
      </div>
    </div>
  );
}