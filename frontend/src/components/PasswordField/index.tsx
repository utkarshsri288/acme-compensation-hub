import { useEffect, useRef, useState } from "react";
import "./styles.css";

type PasswordFieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: "current-password" | "new-password";
  name: string;
  minLength?: number;
  preventAutofill?: boolean;
  describedBy?: string;
};

export default function PasswordField({ label, value, onChange, autoComplete, name, minLength, preventAutofill = false, describedBy }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false);
  const [ready, setReady] = useState(!preventAutofill);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!preventAutofill || ready) return;
    const clearBrowserAutofill = () => {
      if (inputRef.current?.value) {
        inputRef.current.value = "";
        onChange("");
      }
    };
    clearBrowserAutofill();
    const timers = [100, 400, 1000].map(delay => window.setTimeout(clearBrowserAutofill, delay));
    return () => timers.forEach(window.clearTimeout);
  }, [preventAutofill, ready, onChange]);

  return <label className="password-label">
    {label}
    <span className="password-field">
      <input
        ref={inputRef}
        type={visible ? "text" : "password"}
        name={name}
        value={value}
        onChange={event => onChange(event.target.value)}
        autoComplete={autoComplete}
        minLength={minLength}
        aria-describedby={describedBy}
        readOnly={!ready}
        data-lpignore={preventAutofill ? "true" : undefined}
        data-1p-ignore={preventAutofill ? "true" : undefined}
        onFocus={() => {
          if (!ready) {
            if (inputRef.current) inputRef.current.value = "";
            onChange("");
            setReady(true);
          }
        }}
        required
      />
      <button
        className="password-toggle"
        type="button"
        aria-label={visible ? "Hide password" : "Show password"}
        aria-pressed={visible}
        onClick={() => setVisible(!visible)}
      >
        {visible
          ? <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18M10.6 5.2A10.6 10.6 0 0 1 12 5c5.1 0 9.1 4.5 10 7a12 12 0 0 1-3.2 4.5M6.2 6.2A12.4 12.4 0 0 0 2 12c.9 2.5 4.9 7 10 7 1.6 0 3.1-.4 4.4-1.1M9.9 9.9a3 3 0 0 0 4.2 4.2" /></svg>
          : <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12c.9-2.5 4.9-7 10-7s9.1 4.5 10 7c-.9 2.5-4.9 7-10 7S2.9 14.5 2 12Z" /><circle cx="12" cy="12" r="3" /></svg>}
      </button>
    </span>
  </label>;
}
