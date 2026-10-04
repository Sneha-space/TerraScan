import React, { useEffect, useState } from "react";
import { CircleCheck, CircleAlert } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import FileDropzone from "../components/uploads/FileDropzone";
import Button from "../components/common/Button";
import { EmptyState, ErrorNotice, SkeletonRows } from "../components/common/Feedback";
import useApi from "../hooks/useApi";
import { listDocuments, uploadDocument } from "../api/endpoints";
import { errorMessage } from "../api/client";
import config from "../config";
import { documentStatusLabel } from "../utils/fields";
import { fileSize, fullDate, plural, timeAgo } from "../utils/format";

const STATUS_DOT = {
  processing: "bg-turmeric animate-pulse",
  done: "bg-seal",
  failed: "bg-correction",
};

// the backend answers 413 / 415 with short codes; say what to do instead
function uploadError(err) {
  const status = err.response?.status;
  if (status === 413) return `That file is over ${config.maxFileSizeMB} MB. Scan at a lower resolution and upload again.`;
  if (status === 415) return "That file isn't a PDF, JPG or PNG. Save the scan in one of those formats and upload again.";
  return errorMessage(err, "The upload didn't go through. Try again.");
}

function Outcome({ doc }) {
  if (doc.status === "processing") {
    return <span className="text-ink-faint">Plots appear once it's read</span>;
  }
  if (doc.status === "failed") {
    return <span className="text-ink-faint">Check the scan is sharp and upload it again</span>;
  }
  return (
    <span>
      {plural(doc.record_count, "plot")}
      {doc.needs_review > 0 && (
        <span className="text-correction">, {doc.needs_review} need review</span>
      )}
    </span>
  );
}

export default function UploadsPage() {
  const { data: docs, loading, error, reload } = useApi(() => listDocuments(), []);
  const [uploading, setUploading] = useState(null); // the File being sent
  const [notice, setNotice] = useState(null); // { ok, text }

  const waiting = docs?.some((d) => d.status === "processing");

  // while a file waits for the machine, check back so it updates by itself
  useEffect(() => {
    if (!waiting) return;
    const timer = setInterval(() => reload({ quiet: true }), 8000);
    return () => clearInterval(timer);
  }, [waiting, reload]);

  const upload = async (file) => {
    setNotice(null);
    if (!config.acceptedFileTypes.includes(file.type)) {
      setNotice({ ok: false, text: `${file.name} isn't a PDF, JPG or PNG.` });
      return;
    }
    if (file.size > config.maxFileSizeMB * 1024 * 1024) {
      setNotice({ ok: false, text: `${file.name} is ${fileSize(file.size)}, over the ${config.maxFileSizeMB} MB limit.` });
      return;
    }
    setUploading(file);
    try {
      await uploadDocument(file);
      setNotice({ ok: true, text: `Uploaded ${file.name}. It's waiting to be read.` });
      reload({ quiet: true });
    } catch (err) {
      setNotice({ ok: false, text: uploadError(err) });
    } finally {
      setUploading(null);
    }
  };

  return (
    <>
      <PageHeader
        title="Uploads"
        description="Add scanned khatians. Each file is read by the machine, then split into one record per plot."
      />

      <FileDropzone onFile={upload} disabled={!!uploading} />

      <div className="mt-3 min-h-6" aria-live="polite">
        {uploading && <p className="text-sm text-ink-soft">Uploading {uploading.name}…</p>}
        {notice && (
          <p className={`flex items-start gap-2 text-sm ${notice.ok ? "text-seal" : "text-correction"}`}>
            {notice.ok ? (
              <CircleCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            ) : (
              <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            )}
            {notice.text}
          </p>
        )}
      </div>

      <h2 className="title mb-3 mt-8 text-lg">Files</h2>

      {loading && <SkeletonRows rows={4} />}
      {error && <ErrorNotice message={error} onRetry={reload} />}
      {docs && docs.length === 0 && (
        <EmptyState title="No files yet">Upload a scanned khatian above to get started.</EmptyState>
      )}

      {docs && docs.length > 0 && (
        <div className="panel overflow-hidden">
          <ul className="divide-y divide-rule-soft">
            {docs.map((doc) => (
              <li
                key={doc.document_id}
                className="grid gap-x-6 gap-y-1 px-5 py-4 sm:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)_minmax(0,1.3fr)_6.5rem] sm:items-center"
              >
                <div className="min-w-0">
                  <p className="truncate font-semibold">{doc.original_filename}</p>
                  <p className="text-xs text-ink-faint">
                    <time dateTime={doc.created_at} title={fullDate(doc.created_at)}>
                      Uploaded {timeAgo(doc.created_at)}
                    </time>
                  </p>
                </div>
                <p className="flex items-center gap-2 text-sm">
                  <span className={`h-2 w-2 shrink-0 rounded-full ${STATUS_DOT[doc.status]}`} aria-hidden="true" />
                  {documentStatusLabel(doc.status)}
                </p>
                <p className="text-sm">
                  <Outcome doc={doc} />
                </p>
                <div className="sm:text-right">
                  {doc.record_count > 0 && (
                    <Button variant="secondary" size="sm" to={`/records?document=${doc.document_id}`}>
                      See plots
                    </Button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {waiting && (
        <p className="mt-3 text-sm text-ink-faint">
          This list updates by itself while a file is waiting to be read.
        </p>
      )}
    </>
  );
}
