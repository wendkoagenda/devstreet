import { useEffect, useState } from "react";

/** Valeur qui ne suit `value` qu'après `delayMs` sans changement (évite une requête à chaque frappe). */
export function useDebouncedValue<T>(value: T, delayMs: number = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
