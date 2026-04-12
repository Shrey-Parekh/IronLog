export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="skeleton h-6 w-3/4 mb-3" />
      <div className="skeleton h-4 w-1/2 mb-4" />
      <div className="skeleton h-4 w-full mb-2" />
      <div className="skeleton h-4 w-5/6" />
    </div>
  )
}

export function ExerciseCardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="skeleton h-6 w-2/3 mb-2" />
          <div className="flex gap-2">
            <div className="skeleton h-5 w-16" />
            <div className="skeleton h-5 w-20" />
          </div>
        </div>
        <div className="skeleton h-3 w-3 rounded-full" />
      </div>
    </div>
  )
}

export function SetRowSkeleton() {
  return (
    <div className="grid grid-cols-[40px_1fr_1fr_80px_48px] gap-3 items-center p-4 rounded-xl bg-bg-raised border-2 border-border-default animate-pulse">
      <div className="skeleton h-6 w-6 rounded" />
      <div className="skeleton h-10 w-full rounded-lg" />
      <div className="skeleton h-10 w-full rounded-lg" />
      <div className="skeleton h-10 w-full rounded-lg" />
      <div className="skeleton h-12 w-12 rounded-xl" />
    </div>
  )
}

export function StatCardSkeleton() {
  return (
    <div className="card-stats animate-pulse">
      <div className="skeleton h-4 w-24 mb-4" />
      <div className="grid grid-cols-2 gap-6">
        <div>
          <div className="skeleton h-10 w-20 mb-2" />
          <div className="skeleton h-3 w-16" />
        </div>
        <div>
          <div className="skeleton h-10 w-20 mb-2" />
          <div className="skeleton h-3 w-16" />
        </div>
      </div>
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="skeleton h-6 w-32 mb-6" />
      <div className="space-y-4">
        <div className="skeleton h-8 w-full rounded" />
        <div className="skeleton h-8 w-4/5 rounded" />
        <div className="skeleton h-8 w-3/4 rounded" />
        <div className="skeleton h-8 w-2/3 rounded" />
      </div>
    </div>
  )
}

export function ListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}
