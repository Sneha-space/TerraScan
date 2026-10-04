import React from "react";
import { Search } from "lucide-react";

export default function SearchField({ value, onChange, label, placeholder }) {
  return (
    <label className="relative block w-full sm:w-80">
      <span className="sr-only">{label}</span>
      <Search
        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint"
        aria-hidden="true"
      />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="h-10 w-full rounded-control border border-rule bg-sheet pl-9 pr-3 text-sm text-ink placeholder:text-ink-faint focus:border-ink focus:outline-none"
      />
    </label>
  );
}

/** Does any of these values contain the search text? Case-insensitive. */
export function matches(query, values) {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return values.some((v) => v && String(v).toLowerCase().includes(needle));
}
