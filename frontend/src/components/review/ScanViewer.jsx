import React, { useEffect, useState } from "react";
import { ExternalLink, FileX } from "lucide-react";
import { getDocumentFile } from "../../api/endpoints";
import { Skeleton } from "../common/Feedback";

/**
 * Fetch an uploaded file for display.
 * status: "loading" | "ready" | "missing" (not in storage) | "error"
 */
export function useScan(documentId) {
  const [scan, setScan] = useState({ status: "loading" });

  useEffect(() => {
    if (documentId == null) return undefined;
    let url = null;
    let cancelled = false;
    setScan({ status: "loading" });
    getDocumentFile(documentId)
      .then((res) => {
        if (cancelled) return;
        url = URL.createObjectURL(res.data);
        setScan({ status: "ready", url, isPdf: res.data.type === "application/pdf" });
      })
      .catch((err) => {
        if (!cancelled) setScan({ status: err.response?.status === 404 ? "missing" : "error" });
      });
    return () => {
      cancelled = true;
      if (url) URL.revokeObjectURL(url);
    };
  }, [documentId]);

  return scan;
}

/** A one-line note when there is no scan to show beside the fields. */
export function ScanNote({ scan, filename }) {
  if (scan.status === "ready") {
    return (
      <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-ink-soft">
        Scan: {filename}
        <a
          href={scan.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 font-semibold text-ink underline decoration-rule underline-offset-4 hover:decoration-ink"
        >
          Open scan <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
        </a>
      </p>
    );
  }
  if (scan.status === "loading") return null;
  return (
    <p className="flex items-start gap-2 text-sm text-ink-soft">
      <FileX className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      {scan.status === "missing"
        ? `The scan of ${filename} isn't stored on this server. Check this record against the paper copy.`
        : `The scan of ${filename} couldn't be loaded. Reload the page to try again.`}
    </p>
  );
}

/** The scan itself, filling its column. */
export default function ScanViewer({ scan, filename }) {
  if (scan.status === "loading") return <Skeleton className="h-full w-full" />;

  return (
    <figure className="panel flex h-full flex-col overflow-hidden">
      <figcaption className="flex items-center justify-between gap-3 border-b border-rule px-4 py-2.5 text-sm">
        <span className="truncate text-ink-soft">{filename}</span>
        <a
          href={scan.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex shrink-0 items-center gap-1 font-semibold text-ink hover:underline"
        >
          Open in a new tab <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
        </a>
      </figcaption>
      {scan.isPdf ? (
        <iframe src={scan.url} title={`Scan of ${filename}`} className="min-h-0 flex-1 bg-rule-soft" />
      ) : (
        <div className="min-h-0 flex-1 overflow-auto bg-rule-soft p-3">
          <img src={scan.url} alt={`Scan of ${filename}`} className="mx-auto w-full max-w-none shadow-sm" />
        </div>
      )}
    </figure>
  );
}
