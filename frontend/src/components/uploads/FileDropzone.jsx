import React, { useRef, useState } from "react";
import { FileUp } from "lucide-react";
import config from "../../config";

/** Drop a file here or choose one. Calls onFile with the File. */
export default function FileDropzone({ onFile, disabled = false }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const take = (file) => {
    if (file && !disabled) onFile(file);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        take(e.dataTransfer.files?.[0]);
      }}
      className={`flex flex-col items-center gap-4 rounded-panel border border-dashed px-6 py-8 text-center transition-colors sm:flex-row sm:text-left ${
        dragging ? "border-ink bg-machine-wash" : "border-ink-faint/50 bg-sheet"
      } ${disabled ? "opacity-60" : ""}`}
    >
      <FileUp className="h-8 w-8 shrink-0 text-ink-soft" aria-hidden="true" />
      <div className="flex-1">
        <p className="font-semibold">Drop a scanned khatian here</p>
        <p className="text-sm text-ink-soft">
          PDF, JPG or PNG, up to {config.maxFileSizeMB} MB.
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        className="sr-only"
        tabIndex={-1}
        disabled={disabled}
        onChange={(e) => {
          take(e.target.files?.[0]);
          e.target.value = ""; // choosing the same file again still fires
        }}
      />
      <button
        type="button"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
        className="h-10 rounded-control border border-rule bg-sheet px-4 text-sm font-semibold text-ink hover:border-ink-faint disabled:cursor-not-allowed"
      >
        Choose a file
      </button>
    </div>
  );
}
