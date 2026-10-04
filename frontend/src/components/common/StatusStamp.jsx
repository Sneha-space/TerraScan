import React from "react";
import { statusLabel } from "../../utils/fields";

const STYLES = {
  needs_review: "border-correction/40 bg-correction-wash text-correction",
  auto_approved: "border-machine/40 bg-machine-wash text-machine",
  verified: "border-seal/40 bg-seal-wash text-seal",
};

/** A record's status, set like an office stamp. */
export default function StatusStamp({ status, className = "" }) {
  return (
    <span
      className={`inline-flex items-center whitespace-nowrap rounded-stamp border px-2 py-px text-xs font-semibold ${STYLES[status] ?? "border-rule text-ink-soft"} ${className}`}
    >
      {statusLabel(status)}
    </span>
  );
}

export const STATUS_DOT = {
  needs_review: "bg-correction",
  auto_approved: "bg-machine",
  verified: "bg-seal",
};
