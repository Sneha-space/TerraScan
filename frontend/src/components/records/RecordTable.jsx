import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Bilingual from "./Bilingual";
import StatusStamp from "../common/StatusStamp";
import { flagSentence } from "../../utils/format";

/**
 * Records from GET /records as a table (wide screens) or a list (phones).
 *
 * mode "queue" explains why each record was flagged; mode "all" shows
 * district, plot area and status instead.
 */
export default function RecordTable({ records, mode = "all", threshold }) {
  const navigate = useNavigate();
  const v = (record, name) => record.values[name] ?? {};

  return (
    <div className="panel overflow-hidden">
      {/* wide screens */}
      <table className="hidden w-full table-fixed text-left md:table">
        <thead>
          <tr className="border-b border-rule text-xs font-semibold text-ink-faint">
            <th scope="col" className="w-[13%] px-5 py-3 font-semibold">Khasra</th>
            <th scope="col" className="w-[24%] px-3 py-3 font-semibold">Owner</th>
            <th scope="col" className="w-[19%] px-3 py-3 font-semibold">Village</th>
            {mode === "queue" ? (
              <th scope="col" className="px-3 py-3 font-semibold">Why it needs review</th>
            ) : (
              <>
                <th scope="col" className="w-[15%] px-3 py-3 font-semibold">District</th>
                <th scope="col" className="w-[10%] px-3 py-3 font-semibold">Plot area</th>
                <th scope="col" className="px-3 py-3 font-semibold">Status</th>
              </>
            )}
            <th scope="col" className="w-12 px-3 py-3"><span className="sr-only">Open</span></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-rule-soft">
          {records.map((record) => (
            <tr
              key={record.record_id}
              onClick={() => navigate(`/records/${record.record_id}`)}
              className="cursor-pointer align-top transition-colors hover:bg-paper"
            >
              <td className="px-5 py-3.5">
                <Link
                  to={`/records/${record.record_id}`}
                  onClick={(e) => e.stopPropagation()}
                  className="block focus-visible:rounded-stamp"
                >
                  <Bilingual {...v(record, "khasra_number")} size="lg" />
                </Link>
              </td>
              <td className="px-3 py-3.5">
                <Bilingual {...v(record, "owner_name")} />
              </td>
              <td className="px-3 py-3.5">
                <Bilingual {...v(record, "village")} />
              </td>
              {mode === "queue" ? (
                <td className="px-3 py-3.5">
                  <p className="text-sm text-correction">{flagSentence(record.flags, threshold)}</p>
                  <p className="mt-0.5 truncate text-xs text-ink-faint">{record.filename}</p>
                </td>
              ) : (
                <>
                  <td className="px-3 py-3.5">
                    <Bilingual {...v(record, "district")} />
                  </td>
                  <td className="tabular px-3 py-3.5">
                    <Bilingual {...v(record, "plot_area")} />
                  </td>
                  <td className="px-3 py-3.5">
                    <StatusStamp status={record.status} />
                    <p className="mt-1 truncate text-xs text-ink-faint">{record.filename}</p>
                  </td>
                </>
              )}
              <td className="px-3 py-3.5 text-ink-faint">
                <ChevronRight className="mt-1 h-4 w-4" aria-hidden="true" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* phones */}
      <ul className="divide-y divide-rule-soft md:hidden">
        {records.map((record) => (
          <li key={record.record_id}>
            <Link
              to={`/records/${record.record_id}`}
              className="flex items-start gap-4 px-4 py-4 hover:bg-paper"
            >
              <div className="w-16 shrink-0">
                <Bilingual {...v(record, "khasra_number")} size="lg" />
              </div>
              <div className="min-w-0 flex-1 space-y-1">
                <Bilingual {...v(record, "owner_name")} />
                {mode === "queue" ? (
                  <p className="text-sm text-correction">{flagSentence(record.flags, threshold)}</p>
                ) : (
                  <StatusStamp status={record.status} />
                )}
                <p className="truncate text-xs text-ink-faint">{record.filename}</p>
              </div>
              <ChevronRight className="mt-1 h-4 w-4 shrink-0 text-ink-faint" aria-hidden="true" />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
