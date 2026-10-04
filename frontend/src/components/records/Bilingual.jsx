import React from "react";
import { langOf } from "../../utils/script";

/**
 * A value as written in the document, with its English underneath. When
 * both are the same (numbers in an English document), shows it once.
 */
export default function Bilingual({ original, value, size = "base", missing = "Not read" }) {
  if (!original && !value) {
    return <span className="text-sm text-ink-faint">{missing}</span>;
  }
  const main = original || value;
  const showEnglish = value && value !== main;
  return (
    <span className="block min-w-0">
      <span lang={langOf(main)} className={`script block truncate text-ink ${size === "lg" ? "text-lg" : ""}`}>
        {main}
      </span>
      {showEnglish && <span className="block truncate text-xs text-ink-faint">{value}</span>}
    </span>
  );
}
