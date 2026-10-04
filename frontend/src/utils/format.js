import { fieldLabel } from "./fields";

export function plural(count, one, many = `${one}s`) {
  return `${count} ${count === 1 ? one : many}`;
}

const relative = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
const STEPS = [
  ["year", 365 * 24 * 3600],
  ["month", 30 * 24 * 3600],
  ["week", 7 * 24 * 3600],
  ["day", 24 * 3600],
  ["hour", 3600],
  ["minute", 60],
];

/** "3 days ago", "yesterday", "just now". */
export function timeAgo(iso) {
  const seconds = (new Date(iso).getTime() - Date.now()) / 1000;
  for (const [unit, size] of STEPS) {
    if (Math.abs(seconds) >= size) return relative.format(Math.round(seconds / size), unit);
  }
  return "just now";
}

export const fullDate = (iso) =>
  new Date(iso).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });

export const fileSize = (bytes) =>
  bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`;

function listOf(words) {
  if (words.length <= 1) return words.join("");
  return `${words.slice(0, -1).join(", ")} and ${words.at(-1)}`;
}

/**
 * Why a record was flagged, as one sentence: "Plot area wasn't read. 5 other
 * fields scored below 80. District doesn't match the government LGD list."
 * A field that wasn't read also scores 0, so it is counted once, as not read.
 */
export function flagSentence(flags, threshold = 80) {
  if (!flags) return "";
  const missing = flags.missing ?? [];
  const low = (flags.low_confidence ?? []).filter((name) => !missing.includes(name));
  // at most one name: the backend stops at the first location level that fails
  const lgd = flags.lgd_unmatched ?? [];
  const parts = [];
  if (missing.length) {
    const names = missing.map((name, i) => {
      const label = fieldLabel(name);
      return i === 0 ? label : label.toLowerCase();
    });
    parts.push(`${listOf(names)} ${missing.length === 1 ? "wasn't" : "weren't"} read.`);
  }
  if (low.length) {
    const other = missing.length ? "other " : "";
    parts.push(
      `${low.length} ${other}${low.length === 1 ? "field" : "fields"} scored below ${threshold}.`
    );
  }
  if (lgd.length) {
    parts.push(`${fieldLabel(lgd[0])} doesn't match the government LGD list.`);
  }
  return parts.join(" ");
}
