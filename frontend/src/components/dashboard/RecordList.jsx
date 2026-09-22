import React from "react";
import { Link } from "react-router-dom";
import EmptyState from "../common/EmptyState";

// OCR can return blank strings; treat them the same as not found
const present = (value) => (value && String(value).trim()) || null;

function NotFound({ children = "not found" }) {
  return <span className="font-normal italic text-gray-400">{children}</span>;
}

// The big text on each row: owner, khasra and survey together tell records apart
function RecordSummary({ record }) {
  const owner = present(record.owner_name);
  const khasra = present(record.khasra_number);
  const survey = present(record.survey_number);

  if (!owner && !khasra && !survey) {
    return (
      <p className="text-sm italic text-gray-400">
        Owner, khasra and survey number not found
      </p>
    );
  }

  return (
    <>
      <p className="text-base font-semibold text-gray-900 truncate">
        {owner || <NotFound>Owner name not found</NotFound>}
      </p>
      <p className="text-sm text-gray-500 mt-0.5 truncate">
        Khasra <span className="font-medium text-gray-800">{khasra || <NotFound />}</span>
        <span className="mx-1.5 text-gray-300">·</span>
        Survey <span className="font-medium text-gray-800">{survey || <NotFound />}</span>
      </p>
    </>
  );
}

export default function RecordList({ title, records = [], emptyTitle, emptyDescription }) {
  if (!records.length) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-900">{title}</h2>
        </div>
        <EmptyState title={emptyTitle} description={emptyDescription} />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-900">{title}</h2>
        <span className="text-sm text-gray-500">{records.length} records</span>
      </div>

      <div className="divide-y divide-gray-50">
        {records.map((record) => (
          <Link
            key={record.record_id}
            to={`/records/${record.record_id}`}
            className="flex items-center justify-between px-6 py-4 hover:bg-emerald-50/40 transition-colors group"
          >
            <div className="min-w-0 flex-1">
              <RecordSummary record={record} />

              <p className="flex items-center gap-1.5 text-xs text-gray-500 mt-1.5 min-w-0">
                <span className="truncate">{record.filename}</span>
                <span className="text-gray-300 shrink-0">·</span>
                <span className="shrink-0">Record #{record.record_number}</span>
                {record.page_number != null && (
                  <>
                    <span className="text-gray-300 shrink-0">·</span>
                    <span className="shrink-0">Page {record.page_number}</span>
                  </>
                )}
              </p>
            </div>

            <svg
              className="w-5 h-5 text-gray-300 group-hover:text-emerald-500 transition-colors shrink-0 ml-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ))}
      </div>
    </div>
  );
}
