import type { HTMLAttributes, ReactNode } from "react";

export default function Card({ children, className = "", ...props }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return <div className={`panel ${className}`.trim()} {...props}>{children}</div>;
}
