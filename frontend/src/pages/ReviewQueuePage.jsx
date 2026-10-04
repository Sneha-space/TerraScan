import React, { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import RecordTable from "../components/records/RecordTable";
import SearchField, { matches } from "../components/common/SearchField";
import Button from "../components/common/Button";
import { EmptyState, ErrorNotice, SkeletonRows } from "../components/common/Feedback";
import useApi from "../hooks/useApi";
import { getStats, listRecords } from "../api/endpoints";
import { plural } from "../utils/format";

export const searchableValues = (record) => [
  record.filename,
  ...Object.values(record.values).flatMap((v) => [v.value, v.original]),
];

export default function ReviewQueuePage() {
  const { data: records, loading, error, reload } = useApi(
    () => listRecords({ status: "needs_review" }),
    []
  );
  const { data: stats } = useApi(() => getStats(), []);
  const [query, setQuery] = useState("");

  const shown = (records ?? []).filter((r) => matches(query, searchableValues(r)));

  return (
    <>
      <PageHeader
        title="Review queue"
        description="Records the machine wasn't sure about, oldest first. Open one to check it against the scan and verify it."
      />

      {loading && <SkeletonRows />}
      {error && <ErrorNotice message={error} onRetry={reload} />}

      {records && records.length === 0 && (
        <EmptyState
          title="Nothing waiting for review"
          action={<Button variant="secondary" to="/records">See all records</Button>}
        >
          Every record has been verified or approved by the machine.
        </EmptyState>
      )}

      {records && records.length > 0 && (
        <>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <SearchField
              value={query}
              onChange={setQuery}
              label="Search the review queue"
              placeholder="Khasra, owner, village or file"
            />
            <p className="text-sm text-ink-soft">
              {query ? `${shown.length} of ${plural(records.length, "record")}` : `${plural(records.length, "record")} waiting`}
            </p>
          </div>
          {shown.length > 0 ? (
            <RecordTable records={shown} mode="queue" threshold={stats?.confidence_threshold} />
          ) : (
            <EmptyState title="No matches">Nothing in the queue matches “{query}”.</EmptyState>
          )}
        </>
      )}
    </>
  );
}
