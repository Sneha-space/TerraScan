import React, { useState } from "react";
import { Pencil, Undo2 } from "lucide-react";
import Button from "../common/Button";
import { englishValue, fieldLabel } from "../../utils/fields";
import { langOf } from "../../utils/script";

// label | value (as written, English under it) | score | action
export const LEDGER_COLUMNS = "md:grid-cols-[9rem_minmax(0,1fr)_4.75rem_6rem]";

/** The machine's score for one field, as a number and a short bar. */
function Score({ value, threshold }) {
  if (value == null) {
    return <span className="text-sm text-ink-faint" title="No score given">—</span>;
  }
  const scale = threshold > 1 ? 100 : 1;
  const low = value < threshold;
  const color = value === 0 ? "text-correction" : low ? "text-turmeric-text" : "text-ink-faint";
  const bar = value === 0 ? "bg-correction" : low ? "bg-turmeric" : "bg-ink-faint/50";
  return (
    <span className={`tabular inline-flex items-center gap-2 text-sm ${color}`}>
      <span className="w-6 text-right">{Math.round(value * (scale === 1 ? 100 : 1))}</span>
      <span className="h-1 w-8 overflow-hidden rounded-full bg-rule-soft" aria-hidden="true">
        <span className={`block h-full ${bar}`} style={{ width: `${Math.min(100, (value / scale) * 100)}%` }} />
      </span>
      {low && <span className="sr-only">below {threshold}</span>}
    </span>
  );
}

/**
 * One language of a value: plain, or - once corrected - the machine's
 * reading struck through with the correction under it in red ink.
 */
function Line({ machine, corrected, large }) {
  const size = large ? "text-lg" : "text-sm";
  if (corrected != null) {
    return (
      <span className="block">
        {machine && (
          <span lang={langOf(machine)} className="script mr-2 text-sm text-ink-faint line-through decoration-correction/60">
            {machine}
          </span>
        )}
        <span lang={langOf(corrected)} className={`script break-words text-correction ${size}`}>
          {corrected}
        </span>
      </span>
    );
  }
  if (!machine) return null;
  return (
    <span lang={langOf(machine)} className={`script block break-words ${large ? "text-lg text-ink" : "text-sm text-ink-soft"}`}>
      {machine}
    </span>
  );
}

/**
 * One field of the review ledger: the value as written with its English,
 * the score, and a correction form. `pending` holds a correction not yet
 * saved.
 */
export default function LedgerRow({ field, pending, critical, threshold, scriptName, readOnly, onChange }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({ original: "", english: "" });

  // what the reviewer sees now: their unsaved fix, else a saved one, else the machine's
  const shownOriginal = pending?.original ?? field.corrected_original;
  const shownEnglish = pending?.english ?? field.corrected_value;
  const machineEnglish = englishValue({ ...field, display_value: field.value });
  const notRead = !field.original_value && !field.value && shownOriginal == null && shownEnglish == null;
  const wasCorrected = field.corrected_original != null || field.corrected_value != null;
  // English that just repeats the original (a name already in English) shows once
  const showEnglish =
    shownEnglish != null || (machineEnglish != null && machineEnglish !== field.original_value);

  const open = () => {
    setDraft({
      original: shownOriginal ?? field.original_value ?? "",
      english: shownEnglish ?? field.value ?? "",
    });
    setEditing(true);
  };

  const apply = (e) => {
    e.preventDefault();
    const change = {};
    const original = draft.original.trim();
    const english = draft.english.trim();
    if (original && original !== (field.display_original ?? "")) change.original = original;
    if (english && english !== (field.display_value ?? "")) change.english = english;
    onChange(field.field_id, Object.keys(change).length ? change : null);
    setEditing(false);
  };

  const label = fieldLabel(field.name);
  const labelId = `field-${field.field_id}`;

  return (
    <li className={`px-4 py-3 sm:px-5 ${pending ? "bg-correction-wash/50" : ""}`}>
      {/* phones: label and button on top, value and score below */}
      <div
        className={`grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 gap-y-1 [grid-template-areas:'label_action'_'value_score'] md:items-start md:[grid-template-areas:'label_value_score_action'] ${LEDGER_COLUMNS}`}
      >
        <span id={labelId} className="flex items-center gap-1.5 pt-1 text-sm text-ink-soft [grid-area:label]">
          {label}
          {critical && notRead && (
            <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-correction" title="Required" aria-hidden="true" />
          )}
        </span>

        <div className="min-w-0 [grid-area:value]">
          {notRead ? (
            <span className={`block pt-1 text-sm ${critical ? "font-semibold text-correction" : "text-ink-faint"}`}>
              {critical ? "Not read. Required." : "Not read"}
            </span>
          ) : (
            <>
              <Line machine={field.original_value} corrected={shownOriginal} large />
              {showEnglish && <Line machine={machineEnglish} corrected={shownEnglish} />}
            </>
          )}
          {(pending || wasCorrected) && !editing && (
            <span className="mt-0.5 block text-xs text-correction">
              {pending ? "Not saved yet. Saved when you verify the record." : "Corrected by an officer."}
            </span>
          )}
        </div>

        <div className="self-start pt-1.5 [grid-area:score] md:pt-1.5">
          <Score value={field.confidence} threshold={threshold} />
        </div>

        <div className="flex justify-end [grid-area:action]">
          {!readOnly && !editing && (
            pending ? (
              <Button variant="quiet" size="sm" onClick={() => onChange(field.field_id, null)}>
                <Undo2 className="h-3.5 w-3.5" aria-hidden="true" />
                Undo
              </Button>
            ) : (
              <Button variant="quiet" size="sm" onClick={open} aria-describedby={labelId}>
                <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
                Correct
              </Button>
            )
          )}
        </div>
      </div>

      {editing && (
        <form
          onSubmit={apply}
          onKeyDown={(e) => e.key === "Escape" && setEditing(false)}
          className="mt-3 rounded-control border border-rule bg-paper p-4 md:ml-[calc(9rem+1rem)]"
          aria-label={`Correct ${label}`}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm">
              <span className="text-ink-soft">As written{scriptName ? ` (${scriptName})` : ""}</span>
              <input
                autoFocus
                value={draft.original}
                lang={langOf(draft.original || field.original_value)}
                onChange={(e) => setDraft((d) => ({ ...d, original: e.target.value }))}
                className="script mt-1 h-11 w-full rounded-control border border-rule bg-sheet px-3 text-lg focus:border-ink focus:outline-none"
              />
            </label>
            <label className="block text-sm">
              <span className="text-ink-soft">English</span>
              <input
                value={draft.english}
                onChange={(e) => setDraft((d) => ({ ...d, english: e.target.value }))}
                className="mt-1 h-11 w-full rounded-control border border-rule bg-sheet px-3 focus:border-ink focus:outline-none"
              />
            </label>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Button type="submit" size="sm">Apply correction</Button>
            <Button variant="quiet" size="sm" onClick={() => setEditing(false)}>Cancel</Button>
            <span className="text-xs text-ink-faint">Saved when you verify the record.</span>
          </div>
        </form>
      )}
    </li>
  );
}
