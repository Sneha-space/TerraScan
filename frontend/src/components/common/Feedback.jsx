// Loading, error and empty states, shared by every screen.

import React from "react";
import { CircleAlert } from "lucide-react";
import Button from "./Button";

export function Skeleton({ className = "" }) {
  return <div className={`animate-pulse rounded-control bg-rule-soft ${className}`} aria-hidden="true" />;
}

/** Placeholder rows while a list loads. */
export function SkeletonRows({ rows = 5 }) {
  return (
    <div className="panel divide-y divide-rule-soft" role="status" aria-label="Loading">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="flex items-center gap-6 px-5 py-4">
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 flex-1" />
          <Skeleton className="hidden h-5 w-32 sm:block" />
        </div>
      ))}
    </div>
  );
}

export function ErrorNotice({ message, onRetry }) {
  return (
    <div className="panel flex flex-col gap-4 border-correction/30 p-5 sm:flex-row sm:items-start" role="alert">
      <CircleAlert className="h-5 w-5 shrink-0 text-correction" aria-hidden="true" />
      <p className="flex-1 text-ink">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={() => onRetry()}>
          Try again
        </Button>
      )}
    </div>
  );
}

export function EmptyState({ title, children, action }) {
  return (
    <div className="panel px-6 py-12 text-center">
      <p className="title text-lg">{title}</p>
      {children && <p className="mx-auto mt-1 max-w-md text-ink-soft">{children}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
