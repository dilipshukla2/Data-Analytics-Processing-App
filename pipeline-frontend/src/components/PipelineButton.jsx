export default function PipelineButton({
  label,
  loadingLabel,
  loading,
  disabled,
  onClick,
  variant = "default",
}) {
  return (
    <button
      className={`btn ${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {loading ? `⏳ ${loadingLabel || label}` : label}
    </button>
  );
}