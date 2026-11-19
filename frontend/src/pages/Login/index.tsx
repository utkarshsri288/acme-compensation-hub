import { useState, type FormEvent } from "react";
import Button from "../../components/Button";
import Card from "../../components/Card";
import PasswordField from "../../components/PasswordField";
import { api, type AuthUser } from "../../shared/api";

export default function Login({ onLogin }: { onLogin: (token: string, user: AuthUser) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await api<{ token: string; user: AuthUser }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      onLogin(result.token, result.user);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  };

  return <div className="login-shell">
    <Card className="login-card">
      <div className="login-mark">ACME <span>Comp Hub</span></div>
      <p className="eyebrow">Internal HR workspace</p>
      <h1>Welcome back</h1>
      <p>Sign in to manage employee compensation and payroll insights.</p>
      <form onSubmit={submit}>
        <label>Username
          <input type="text" value={username} onChange={event => setUsername(event.target.value)} autoComplete="username" required />
        </label>
        <PasswordField label="Password" name="password" value={password} onChange={setPassword} autoComplete="current-password" />
        {error && <div className="login-error" role="alert">{error}</div>}
        <Button type="submit" disabled={loading}>{loading ? "Signing in…" : "Sign in to workspace"}</Button>
      </form>
      {import.meta.env.DEV && <div className="demo-hint">
        <b>Demo Admin</b>
        <span>acme_admin</span>
        <span>AcmeHR2026!</span>
      </div>}
    </Card>
  </div>;
}
