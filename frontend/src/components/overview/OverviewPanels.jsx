import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Bilingual from "../records/Bilingual";
import { STATUS_DOT } from "../common/StatusStamp";
import { fieldLabel, statusLabel } from "../../utils/fields";
import { flagSentence, plural } from "../../utils/format";
import { langOf } from "../../utils/script";

const ORDER = ["verified", "auto_approved", "needs_review"];
const pct = (part, whole) => (whole ? Math.round((part / whole) * 100) : 0);

function PanelTitle({ children, action }) {
  return (
    <div className="mb-4 flex items-baseline justify-between gap-4">
      <h2 className="title text-lg">{children}</h2>
      {action}
    </div>
  );
}

function TextLink({ to, children }) {
  return (
    <Link
      to={to}
      className="inline-flex shrink-0 items-center gap-0.5 text-sm text-ink-soft underline decoration-rule underline-offset-4 hover:text-ink hover:decoration-ink"
    >
      {children}
    </Link>
  );
}

/** Where every record stands: one bar from verified to waiting. */
export function PipelinePanel({ stats }) {
  const { records, documents } = stats;
  // the bar grows in once on load; the global reduced-motion rule turns this off
  const [grown, setGrown] = useState(false);
  useEffect(() => {
    const frame = requestAnimationFrame(() => setGrown(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  const read = documents.done;
  const problems = [
    documents.failed && `${plural(documents.failed, "file")} couldn't be read`,
    documents.processing && `${plural(documents.processing, "file")} ${documents.processing === 1 ? "is" : "are"} waiting to be read`,
  ].filter(Boolean);

  return (
    <section className="panel p-6 sm:p-8" aria-labelledby="pipeline-title">
      <h2 id="pipeline-title" className="title max-w-3xl text-xl [text-wrap:balance] sm:text-2xl">
        {records.total === 0
          ? "No records yet. Upload a scanned khatian to start."
          : `${plural(records.total, "record")} read from ${plural(read, "file")}. ${
              records.needs_review === 0
                ? "None are waiting for an officer."
                : `${records.needs_review} ${records.needs_review === 1 ? "is" : "are"} waiting for an officer.`
            }`}
      </h2>

      {records.total > 0 && (
        <>
          <div className="mt-6 flex h-3 overflow-hidden rounded-stamp bg-rule-soft" aria-hidden="true">
            {ORDER.map((status) => (
              <div
                key={status}
                className={`${STATUS_DOT[status]} transition-[width] duration-700 ease-out first:rounded-l-stamp last:rounded-r-stamp [&:not(:last-child)]:mr-0.5`}
                style={{ width: grown ? `${pct(records[status], records.total)}%` : "0%" }}
              />
            ))}
          </div>

          <ul className="mt-5 grid grid-cols-3 gap-3 sm:gap-4">
            {ORDER.map((status) => (
              <li key={status}>
                <Link
                  to={status === "needs_review" ? "/review" : `/records?status=${status}`}
                  className="group block rounded-control"
                >
                  <span className="flex items-center gap-2 text-sm text-ink-soft group-hover:text-ink">
                    <span className={`h-2.5 w-2.5 rounded-sm ${STATUS_DOT[status]}`} aria-hidden="true" />
                    {statusLabel(status)}
                  </span>
                  <span className="tabular mt-1 flex items-baseline gap-2">
                    <span className="title text-2xl">{records[status]}</span>
                    <span className="text-sm text-ink-faint">{pct(records[status], records.total)}%</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}

      {problems.length > 0 && (
        <p className="mt-6 border-t border-rule-soft pt-4 text-sm text-ink-soft">
          Also: {problems.join(", ")}. <TextLink to="/uploads">See uploads</TextLink>
        </p>
      )}
    </section>
  );
}

/** How often officers had to change what the machine read, field by field. */
export function AccuracyPanel({ stats }) {
  const { fields_checked: checked, fields_corrected: corrected } = stats.accuracy;
  const fields = stats.corrections_by_field.filter((f) => f.corrected > 0).slice(0, 5);

  return (
    <section className="panel p-6" aria-labelledby="accuracy-title">
      <PanelTitle>
        <span id="accuracy-title">Machine accuracy</span>
      </PanelTitle>

      {checked === 0 ? (
        <p className="text-ink-soft">
          Nothing verified yet. Once an officer verifies a record, this shows how much of what the
          machine read was right.
        </p>
      ) : (
        <>
          <p className="text-ink-soft">
            Officers checked {plural(checked, "field")} on {plural(stats.records.verified, "verified record")}.
          </p>
          <p className="tabular mt-3 flex items-baseline gap-3">
            <span className="title text-3xl">{pct(checked - corrected, checked)}%</span>
            <span className="text-ink-soft">kept exactly as read</span>
          </p>

          {fields.length > 0 && (
            <>
              <h3 className="mb-3 mt-6 text-sm font-semibold text-ink-soft">Corrected most often</h3>
              <ul className="space-y-3">
                {fields.map((f) => (
                  <li key={f.name} className="grid grid-cols-[8.5rem_minmax(0,1fr)_auto] items-center gap-3 text-sm">
                    <span className="truncate">{fieldLabel(f.name)}</span>
                    <span className="h-2 overflow-hidden rounded-stamp bg-rule-soft" aria-hidden="true">
                      <span
                        className="block h-full rounded-stamp bg-correction"
                        style={{ width: `${pct(f.corrected, f.checked)}%` }}
                      />
                    </span>
                    <span className="tabular text-ink-soft">
                      {f.corrected} of {f.checked}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </section>
  );
}

/** Records per district, split by status. */
export function DistrictPanel({ stats }) {
  const districts = stats.districts;
  const largest = Math.max(1, ...districts.map((d) => d.total));

  return (
    <section className="panel p-6" aria-labelledby="district-title">
      <PanelTitle>
        <span id="district-title">Districts</span>
      </PanelTitle>

      {districts.length === 0 ? (
        <p className="text-ink-soft">Districts appear once records have been read.</p>
      ) : (
        <ul className="space-y-4">
          {districts.map((d) => (
            <li key={d.original ?? "unknown"} className="grid grid-cols-[minmax(0,9.5rem)_minmax(0,1fr)_2.5rem] items-center gap-3">
              <span className="min-w-0">
                {d.original ? (
                  <>
                    <span lang={langOf(d.original)} className="script block truncate">{d.original}</span>
                    <span className="block truncate text-xs text-ink-faint">{d.value}</span>
                  </>
                ) : (
                  <span className="text-ink-faint">District not read</span>
                )}
              </span>
              <span className="flex h-2 overflow-hidden rounded-stamp" style={{ width: `${pct(d.total, largest)}%` }}>
                {ORDER.map((status) =>
                  d[status] ? (
                    <span
                      key={status}
                      className={`${STATUS_DOT[status]} [&:not(:last-child)]:mr-px`}
                      style={{ width: `${pct(d[status], d.total)}%` }}
                      title={`${statusLabel(status)}: ${d[status]}`}
                    />
                  ) : null
                )}
              </span>
              <span className="tabular text-right text-sm text-ink-soft">
                {d.total}
                <span className="sr-only">
                  {" "}records: {ORDER.map((s) => `${d[s]} ${statusLabel(s).toLowerCase()}`).join(", ")}
                </span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

/** The records that have waited longest for an officer. */
export function WaitingPanel({ records, threshold }) {
  return (
    <section className="panel p-6" aria-labelledby="waiting-title">
      <PanelTitle action={records.length > 0 && <TextLink to="/review">Open review queue</TextLink>}>
        <span id="waiting-title">Waiting longest</span>
      </PanelTitle>

      {records.length === 0 ? (
        <p className="text-ink-soft">Nothing is waiting. Every record has been verified or approved.</p>
      ) : (
        <ul className="-mx-2 divide-y divide-rule-soft">
          {records.map((r) => (
            <li key={r.record_id}>
              <Link
                to={`/records/${r.record_id}`}
                className="grid grid-cols-[4.5rem_minmax(0,1fr)_auto] items-start gap-4 rounded-control px-2 py-3 hover:bg-paper"
              >
                <Bilingual {...r.values.khasra_number} size="lg" />
                <span className="min-w-0">
                  <Bilingual {...r.values.owner_name} />
                  <span className="mt-1 block text-sm text-correction">{flagSentence(r.flags, threshold)}</span>
                </span>
                <ChevronRight className="mt-1.5 h-4 w-4 text-ink-faint" aria-hidden="true" />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
