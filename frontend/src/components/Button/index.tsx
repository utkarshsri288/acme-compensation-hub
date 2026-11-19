import type { ButtonHTMLAttributes } from "react";

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export default function Button({ children, variant = "primary", className = "", ...props }: ButtonProps) {
  return <button className={`${variant === "ghost" ? "ghost" : ""} ${className}`.trim()} {...props}>{children}</button>;
}
