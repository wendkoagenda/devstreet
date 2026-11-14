import * as React from "react"

import { cn } from "@/lib/utils"

/** Accepte `null` (RHF / Zod nullable) en le normalisant vers chaîne vide. */
type InputProps = Omit<React.ComponentProps<"input">, "value"> & {
  value?: React.ComponentProps<"input">["value"] | null
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, value, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          className
        )}
        ref={ref}
        {...props}
        value={value === null ? "" : value}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
