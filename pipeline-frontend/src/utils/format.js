export const formatNumber = (n) => {
  if (n === null || n === undefined) return "—";
  if (typeof n !== "number") return String(n);
  return n.toLocaleString();
};

export const formatMoney = (n) => {
  if (n === null || n === undefined) return "—";
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
};

export const formatHash = (hash, len = 12) => {
  if (!hash) return "—";
  return hash.length > len ? `${hash.slice(0, len)}…` : hash;
};

export const formatDateTime = (iso) => {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
};

export const humanLabel = (key) =>
  key
    .replace(/([A-Z])/g, " $1")
    .replace(/_/g, " ")
    .replace(/^./, (s) => s.toUpperCase())
    .trim();