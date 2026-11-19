import type { ReactNode } from "react";
import Card from "../Card";
import Button from "../Button";

type DataTableProps = { children: ReactNode; className?: string };

export default function DataTable({ children, className = "" }: DataTableProps) {
  return <Card className={`table-panel ${className}`.trim()}>{children}</Card>;
}

export function TableState({ message, error = false }: { message: string; error?: boolean }) {
  return <div className={`state ${error ? "error" : ""}`} role={error ? "alert" : "status"}>{message}</div>;
}

export function Pagination({ page, pages, onPageChange }: { page: number; pages: number; onPageChange: (page: number) => void }) {
  if (pages <= 1) return null;
  const start = Math.max(1, Math.min(pages - 4, page - 2));
  const numbers = Array.from({ length: Math.min(5, pages) }, (_, index) => start + index);
  return <nav className="pagination" aria-label="Employee pages">
    <Button variant="ghost" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>← Previous</Button>
    <div className="page-numbers">{numbers.map(number => <Button variant={number === page ? "primary" : "ghost"} key={number} aria-current={number === page ? "page" : undefined} onClick={() => onPageChange(number)}>{number}</Button>)}</div>
    <Button variant="ghost" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>Next →</Button>
  </nav>;
}
