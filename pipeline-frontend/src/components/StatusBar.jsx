export default function StatusBar({ text, isLoading, error }) {
  if (error) {
    return <div className="error-bar">❌ {error}</div>;
  }
  if (!text) return null;

  return (
    <div className="status-bar">
      {isLoading && <span className="dot" />}
      {text}
    </div>
  );
}