import { useState } from "react";
import Button from "../Button";

type Props = { page: number; sort: string; direction: "asc" | "desc"; search: string; country: string; department: string; status: string };

export default function EmployeeExport({ page, sort, direction, search, country, department, status }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const download = async () => {
    setBusy(true);
    setError("");
    try {
      const params = new URLSearchParams({ page: String(page), page_size: "12", sort, direction, search, country, department, status });
      const response = await fetch(`/api/employees/export?${params}`, { headers: { Authorization: `Token ${localStorage.getItem("acme_token") ?? ""}` } });
      if (!response.ok) throw new Error("Export failed. Please try again.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = `acme-employees-page-${page}.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Export failed.");
    } finally {
      setBusy(false);
    }
  };
  return <div><Button onClick={download} disabled={busy}>{busy ? "Exporting…" : "Export current view ↓"}</Button>{error && <p role="alert">{error}</p>}</div>;
}
