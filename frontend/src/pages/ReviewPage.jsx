import React, { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ChevronLeft, ChevronRight, CircleCheck } from "lucide-react";
import Button from "../components/common/Button";
import StatusStamp from "../components/common/StatusStamp";
import { ErrorNotice, Skeleton } from "../components/common/Feedback";
import LedgerRow, { LEDGER_COLUMNS } from "../components/review/LedgerRow";
import ScanViewer, { ScanNote, useScan } from "../components/review/ScanViewer";
import { RECORDS_CHANGED } from "../components/layout/AppShell";
import useApi from "../hooks/useApi";
import { listRecords, getRecord, verifyRecord } from "../api/endpoints";
import { errorMessage } from "../api/client";
import { groupFields } from "../utils/fields";
import { flagSentence, plural } from "../utils/format";
import { langOf, mainScript } from "../utils/script";

/** "Plot 2 of 9", with links to the neighbouring plots of the same khatian. */
function PlotStepper({ siblings, recordId }) {
  if (!siblings || siblings.length < 2) return null;
  const index = siblings.findIndex((r) => r.record_id === recordId);
  if (index === -1) return null;
  const prev = siblings[index - 1];
  const next = siblings[index + 1];
  const step = (record, label, Icon) =>
    record ? (
      <Link
        to={`/records/${record.record_id}`}
        aria-label={`${label}: khasra ${record.values.khasra_number?.value ?? record.record_number}`}
        className="flex h-9 w-9 items-center justify-center rounded-control border border-rule bg-sheet text-ink hover:border-ink-faint"
      >
        <Icon className="h-4 w-4" aria-hidden="true" />
      </Link>
    ) : (
      <span className="flex h-9 w-9 items-center justify-center rounded-control border border-rule-soft text-rule" aria-hidden="true">
        <Icon className="h-4 w-4" />
      </span>
    );

  return (
    <nav className="flex items-center gap-2" aria-label="Plots in this khatian">
      {step(prev, "Previous plot", ChevronLeft)}
      <span className="tabular px-1 text-sm text-ink-soft">
        Plot {index + 1} of {siblings.length}
      </span>
      {step(next, "Next plot", ChevronRight)}
    </nav>
  );
}

function Fact({ label, original, value }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-ink-faint">{label}</dt>
      <dd className="mt-0.5">
        {original || value ? (
          <>
            <span lang={langOf(original || value)} className="script block truncate">{original || value}</span>
            {original && value && value !== original && (
              <span className="block truncate text-xs text-ink-faint">{value}</span>
            )}
          </>
        ) : (
          <span className="text-sm text-ink-faint">Not read</span>
        )}
      </dd>
    </div>
  );
}

/** Why the record is in its current state, in one or two sentences. */
function StatusNote({ record, correctedCount }) {
  if (record.status === "needs_review") {
    return <p className="text-correction">{flagSentence(record.flags, record.confidence_threshold)}</p>;
  }
  if (record.status === "auto_approved") {
    return (
      <p className="text-ink-soft">
        Approved by the machine: every required field was read and every score is{" "}
        {record.confidence_threshold} or above. You can still correct and verify it.
      </p>
    );
  }
  return (
    <p className="text-seal">
      {correctedCount > 0
        ? `Verified by an officer, with ${plural(correctedCount, "field")} corrected. Corrections are in red.`
        : "Verified by an officer and accepted as read."}
    </p>
  );
}

export default function ReviewPage() {
  const recordId = Number(useParams().recordId);
  const record = useApi(() => getRecord(recordId), [recordId]);
  const documentId = record.data?.document_id;
  const siblings = useApi(
    () => (documentId == null ? Promise.resolve({ data: null }) : listRecords({ document_id: documentId })),
    [documentId]
  );
  const scan = useScan(documentId);

  const [pending, setPending] = useState({}); // field_id -> { original?, english? }
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [verified, setVerified] = useState(null); // { count, next } after a verify in this visit

  useEffect(() => {
    setPending({});
    setSaveError(null);
    setVerified(null);
  }, [recordId]);

  const data = record.data;
  const fields = data?.fields ?? [];
  const byName = useMemo(() => Object.fromEntries(fields.map((f) => [f.name, f])), [fields]);
  const groups = useMemo(() => groupFields(fields), [fields]);
  const script = useMemo(() => mainScript(fields.map((f) => f.original_value)), [fields]);
  const pendingCount = Object.keys(pending).length;
  const correctedCount = fields.filter((f) => f.corrected_value != null || f.corrected_original != null).length;

  const setCorrection = (fieldId, change) =>
    setPending((prev) => {
      const next = { ...prev };
      if (change) next[fieldId] = change;
      else delete next[fieldId];
      return next;
    });

  const khasra = byName.khasra_number;
  const khasraName = khasra?.display_value ?? khasra?.display_original ?? `record ${data?.record_number}`;

  const verify = async () => {
    setSaving(true);
    setSaveError(null);
    const corrections = Object.entries(pending).map(([fieldId, c]) => ({
      field_id: Number(fieldId),
      ...(c.english !== undefined && { corrected_value: c.english }),
      ...(c.original !== undefined && { corrected_original: c.original }),
    }));
    try {
      await verifyRecord(recordId, corrections);
      const queue = await listRecords({ status: "needs_review", limit: 2 }).catch(() => ({ data: [] }));
      setVerified({
        count: corrections.length,
        next: queue.data.find((r) => r.record_id !== recordId) ?? null,
      });
      setPending({});
      record.reload({ quiet: true });
      siblings.reload({ quiet: true });
      window.dispatchEvent(new Event(RECORDS_CHANGED));
    } catch (err) {
      setSaveError(errorMessage(err, "The record couldn't be verified. Try again."));
    } finally {
      setSaving(false);
    }
  };

  if (record.loading) {
    return (
      <div className="space-y-6" role="status" aria-label="Loading">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-28 w-full max-w-3xl" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }
  if (record.error) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Link to="/review" className="inline-flex items-center gap-1.5 text-sm text-ink-soft hover:text-ink">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Review queue
        </Link>
        <ErrorNotice message={record.error} onRetry={record.reload} />
      </div>
    );
  }

  const readOnly = data.status === "verified";
  const showScan = scan.status === "ready" || scan.status === "loading";
  // where the officer came from, so verifying doesn't change the back link
  const back =
    data.status === "needs_review" || verified
      ? { to: "/review", label: "Review queue" }
      : { to: "/records", label: "Records" };

  return (
    <div
      className={
        showScan
          ? "mx-auto max-w-[112rem] xl:grid xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] xl:gap-8"
          : "mx-auto max-w-5xl"
      }
    >
      {showScan && (
        <div className="hidden xl:block">
          <div className="sticky top-8 h-[calc(100vh-4rem)]">
            <ScanViewer scan={scan} filename={data.filename} />
          </div>
        </div>
      )}

      <div className="min-w-0">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link to={back.to} className="inline-flex items-center gap-1.5 text-sm text-ink-soft hover:text-ink">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" /> {back.label}
          </Link>
          <PlotStepper siblings={siblings.data} recordId={recordId} />
        </div>

        {/* who and where */}
        <header className="mt-5 border-b border-rule pb-6">
          <div className="flex flex-wrap items-end gap-x-4 gap-y-2">
            <div>
              <p className="text-sm text-ink-faint">Khasra</p>
              <h1 className="title flex items-baseline gap-3 text-3xl">
                <span lang={langOf(khasra?.display_original)} className="script">
                  {khasra?.display_original ?? khasra?.display_value ?? "Not read"}
                </span>
                {khasra?.display_original && khasra?.display_value && (
                  <span className="text-xl font-normal text-ink-faint">{khasra.display_value}</span>
                )}
              </h1>
            </div>
            <StatusStamp status={data.status} className="mb-1.5" />
          </div>

          <dl
            className={`mt-5 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4 ${showScan ? "xl:grid-cols-2 2xl:grid-cols-4" : ""}`}
          >
            <Fact label="Owner" original={byName.owner_name?.display_original} value={byName.owner_name?.display_value} />
            <Fact label="Village (mouza)" original={byName.village?.display_original} value={byName.village?.display_value} />
            <Fact label="District" original={byName.district?.display_original} value={byName.district?.display_value} />
            <Fact label="Khata number" original={byName.khata_number?.display_original} value={byName.khata_number?.display_value} />
          </dl>

          <div className="mt-5 space-y-2">
            <StatusNote record={data} correctedCount={correctedCount} />
            <div className={showScan ? "xl:hidden" : ""}>
              <ScanNote scan={scan} filename={data.filename} />
            </div>
          </div>
        </header>

        {/* the ledger */}
        <div className="mt-6 space-y-6">
          <div className={`hidden gap-x-4 px-5 text-xs text-ink-faint md:grid ${LEDGER_COLUMNS}`}>
            <span>Field</span>
            <span>As written{script ? ` (${script.name})` : ""} and English</span>
            <span>Score</span>
            <span />
          </div>

          {groups.map((group) => (
            <section key={group.title} aria-labelledby={`group-${group.title}`}>
              <h2 id={`group-${group.title}`} className="title mb-2 px-1 text-base">
                {group.title}
              </h2>
              <ul className="panel divide-y divide-rule-soft">
                {group.fields.map((field) => (
                  <LedgerRow
                    key={field.field_id}
                    field={field}
                    pending={pending[field.field_id]}
                    critical={data.critical_fields?.includes(field.name)}
                    threshold={data.confidence_threshold}
                    scriptName={script?.name}
                    readOnly={readOnly}
                    onChange={setCorrection}
                  />
                ))}
              </ul>
            </section>
          ))}
        </div>

        {/* verify - nothing to do on a record verified before this visit */}
        {(!readOnly || verified) && (
        <div className="sticky bottom-0 z-10 -mx-4 mt-6 border-t border-rule bg-paper/95 px-4 py-4 backdrop-blur sm:mx-0 sm:px-0">
          {verified ? (
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between" role="status">
              <p className="flex items-center gap-2 font-semibold text-seal">
                <CircleCheck className="h-5 w-5" aria-hidden="true" />
                Khasra {khasraName} verified
                {verified.count > 0 ? ` with ${plural(verified.count, "correction")}.` : "."}
              </p>
              <div className="flex gap-2">
                {verified.next ? (
                  <Button to={`/records/${verified.next.record_id}`}>Next in review queue</Button>
                ) : (
                  <Button to="/">Queue is empty. Back to overview</Button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm">
                {saveError ? (
                  <p className="text-correction" role="alert">{saveError}</p>
                ) : pendingCount > 0 ? (
                  <p className="text-ink">{plural(pendingCount, "correction")} will be saved when you verify.</p>
                ) : (
                  <p className="text-ink-soft">No corrections. Verifying accepts the record as read.</p>
                )}
              </div>
              <Button onClick={verify} loading={saving}>
                Verify khasra {khasraName}
              </Button>
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  );
}
