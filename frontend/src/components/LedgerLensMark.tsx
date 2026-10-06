export function LedgerLensMark({ compact = false }: { compact?: boolean }) {
  return (
    <span className={compact ? "brand-mark compact" : "brand-mark"} aria-hidden="true">
      <svg viewBox="0 0 64 64" role="img">
        <circle cx="32" cy="32" r="27" />
        <path d="M19 16v31h15M26 13v28l10 9" />
        <path d="M37 23h12M37 31h12M37 39h12" />
      </svg>
    </span>
  );
}
