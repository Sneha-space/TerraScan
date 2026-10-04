import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { X } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import RecordTable from "../components/records/RecordTable";
import SearchField, { matches } from "../components/common/SearchField";
import { EmptyState, ErrorNotice, SkeletonRows } from "../components/common/Feedback";
import useApi from "../hooks/useApi";
import { listRecords } from "../api/endpoints";
import { plural } from "../utils/format";
import { searchableValues } from "./ReviewQueuePage";

const FILTERS = [
  { key: "", label: "All" },
  { key: "needs_review", label: "Needs review" },
  { key: "auto_approved", label: "Auto-approved" },
  { key: "verified", label: "Verified" },
];

export default function RecordsPage() {
  const [params, setParams] = useSearchParams();
  const status = params.get("status") ?? "";
  const documentId = params.get("document");
  const [query, setQuery] = useState("");

  const { data: records, loading, error, reload } = useApi(() => listRecords(), []);

  const setParam = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  };

  const inDocument = (records ?? []).filter(
    (r) => !documentId || String(r.document_id) === documentId
  );
  const countFor = (key) => inDocument.filter((r) => !key || r.status === key).length;
  // newest file first; plots of one file stay in order
  const shown = inDocument
    .filter((r) => !status || r.status === status)
    .filter((r) => matches(query, searchableValues(r)))
    .sort((a, b) => b.document_id - a.document_id || a.record_number - b.record_number);

  const documentName = documentId && inDocument[0]?.filename;

  return (
    <>
      <PageHeader
        title="Records"
        description="Every plot read from every file. A khatian with nine plots becomes nine records."
      />

      {loading && <SkeletonRows rows={8} />}
      {error && <ErrorNotice message={error} onRetry={reload} />}

      {records && (
        <>
          {documentId && (
            <p className="mb-4 inline-flex items-center gap-2 rounded-control border border-rule bg-sheet py-1 pl-3 pr-1 text-sm">
              <span>
                Plots from <span className="font-semibold">{documentName ?? `file ${documentId}`}</span>
              </span>
              <button
                type="button"
                onClick={() => setParam("document", null)}
                className="flex h-7 w-7 items-center justify-center rounded-stamp text-ink-faint hover:bg-rule-soft hover:text-ink"
                aria-label="Show records from every file"
              >
                <X className="h-4 w-4" />
              </button>
            </p>
          )}

          <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div
              className="inline-flex w-full overflow-x-auto rounded-control border border-rule bg-sheet p-1 sm:w-auto"
              role="group"
              aria-label="Filter by status"
            >
              {FILTERS.map((f) => (
                <button
                  key={f.key}
                  type="button"
                  onClick={() => setParam("status", f.key)}
                  aria-pressed={status === f.key}
                  className={`flex h-8 shrink-0 items-center gap-1.5 rounded-stamp px-3 text-sm transition-colors ${
                    status === f.key ? "bg-ink font-semibold text-white" : "text-ink-soft hover:text-ink"
                  }`}
                >
                  {f.label}
                  <span className={`tabular text-xs ${status === f.key ? "text-white/70" : "text-ink-faint"}`}>
                    {countFor(f.key)}
                  </span>
                </button>
              ))}
            </div>
            <SearchField
              value={query}
              onChange={setQuery}
              label="Search records"
              placeholder="Khasra, owner, village or file"
            />
          </div>

          {shown.length > 0 ? (
            <>
              <RecordTable records={shown} mode="all" />
              <p className="mt-3 text-sm text-ink-faint">Showing {plural(shown.length, "record")}</p>
            </>
          ) : records.length === 0 ? (
            <EmptyState title="No records yet">
              Records appear here once an uploaded file has been read.
            </EmptyState>
          ) : (
            <EmptyState title="No matching records">Try another status or search.</EmptyState>
          )}
        </>
      )}
    </>
  );
}
