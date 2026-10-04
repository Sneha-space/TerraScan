import React from "react";
import { Link } from "react-router-dom";
import { LoaderCircle } from "lucide-react";

const VARIANTS = {
  primary: "bg-ink text-white hover:bg-ink-hover border border-ink",
  secondary: "bg-sheet text-ink border border-rule hover:border-ink-faint",
  quiet: "bg-transparent text-ink-soft border border-transparent hover:text-ink hover:bg-rule-soft",
};

const SIZES = {
  sm: "h-8 px-3 text-sm gap-1.5",
  md: "h-10 px-4 text-sm gap-2",
};

/**
 * A button, or a link styled as one when `to` is given.
 */
export default function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  to,
  className = "",
  type = "button",
  ...props
}) {
  const classes = `inline-flex items-center justify-center whitespace-nowrap rounded-control font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant]} ${SIZES[size]} ${className}`;

  if (to) {
    return (
      <Link to={to} className={classes} {...props}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} disabled={disabled || loading} className={classes} {...props}>
      {loading && <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />}
      {children}
    </button>
  );
}
