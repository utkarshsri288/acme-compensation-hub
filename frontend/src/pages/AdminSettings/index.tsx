import { useEffect, useRef, useState, type FormEvent } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Button from "../../components/Button";
import PasswordField from "../../components/PasswordField";
import { api, type AdminUser } from "../../shared/api";
import { passwordChecks } from "../../shared/password";

export default function AdminSettingsPage({ currentUserId, onLogout }: { currentUserId: number; onLogout: () => void }) {
  const client = useQueryClient();
  const users = useQuery({ queryKey: ["admin-users"], queryFn: () => api<AdminUser[]>("/api/admin/users") });
  const [showForm, setShowForm] = useState(false);
  const [username, setUsername] = useState("");
  const [usernameReady, setUsernameReady] = useState(false);
  const usernameRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  useEffect(() => {
    if (!showForm || usernameReady) return;
    const clearBrowserAutofill = () => {
      if (usernameRef.current?.value) {
        usernameRef.current.value = "";
        setUsername("");
      }
    };
    clearBrowserAutofill();
    const timers = [100, 400, 1000].map(delay => window.setTimeout(clearBrowserAutofill, delay));
    return () => timers.forEach(window.clearTimeout);
  }, [showForm, usernameReady]);

  const clearForm = () => {
    setUsername("");
    setUsernameReady(false);
    setName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
  };
  const toggleForm = () => {
    clearForm();
    setError("");
    setShowForm(!showForm);
  };

  const createUser = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    if (!passwordChecks(password, username).every(check => check.valid) || password !== confirmPassword) {
      setError("Complete the password requirements and confirm the same password.");
      return;
    }
    try {
      await api("/api/admin/users", { method: "POST", body: JSON.stringify({ username, name, email, password }) });
      clearForm();
      setShowForm(false);
      await client.invalidateQueries({ queryKey: ["admin-users"] });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to create user.");
    }
  };

  const checks = passwordChecks(password, username);
  const passwordReady = checks.every(check => check.valid);
  const confirmationReady = confirmPassword.length > 0 && password === confirmPassword;
  const formReady = /^[a-z][a-z0-9_.-]{2,29}$/i.test(username) && Boolean(name.trim()) && Boolean(email.trim()) && passwordReady && confirmationReady;

  const toggle = async (user: AdminUser) => {
    setError("");
    setBusyId(user.id);
    try {
      await api(`/api/admin/users/${user.id}`, { method: "PATCH", body: JSON.stringify({ is_active: !user.is_active }) });
      await client.invalidateQueries({ queryKey: ["admin-users"] });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update user.");
    } finally {
      setBusyId(null);
    }
  };

  const transfer = async (user: AdminUser) => {
    if (!window.confirm(`Transfer administrator role to ${user.name}? You will be signed out.`)) return;
    setError("");
    setBusyId(user.id);
    try {
      await api(`/api/admin/users/${user.id}`, { method: "PATCH", body: JSON.stringify({ transfer_admin: true }) });
      onLogout();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to transfer administrator role.");
      setBusyId(null);
    }
  };

  return <>
    <div className="heading">
      <div>
        <p className="eyebrow">Access control</p>
        <h1>Admin settings</h1>
        <p>Create HR Manager accounts and transfer the Administrator role when ownership changes.</p>
      </div>
      <Button onClick={toggleForm}>{showForm ? "Close form" : "Create HR user +"}</Button>
    </div>
    {showForm && <form className="user-form panel" onSubmit={createUser} autoComplete="off">
      <h3>Create HR Manager</h3>
      <div className="user-form-grid">
        <label>Username<input ref={usernameRef} name="new-username" value={username} onChange={event => setUsername(event.target.value)} onFocus={() => { if (!usernameReady) { if (usernameRef.current) usernameRef.current.value = ""; setUsername(""); setUsernameReady(true); } }} readOnly={!usernameReady} data-lpignore="true" data-1p-ignore="true" minLength={3} maxLength={30} pattern="[A-Za-z][A-Za-z0-9_.-]{2,29}" autoComplete="off" required /></label>
        <label>Full name<input name="new-full-name" value={name} onChange={event => setName(event.target.value)} autoComplete="off" required /></label>
        <label>Work email<input name="new-email" type="email" value={email} onChange={event => setEmail(event.target.value)} autoComplete="off" required /></label>
        <PasswordField label="Password" name="new-user-password" value={password} onChange={setPassword} autoComplete="new-password" minLength={8} preventAutofill describedBy="password-requirements" />
        <PasswordField label="Confirm password" name="confirm-new-user-password" value={confirmPassword} onChange={setConfirmPassword} autoComplete="new-password" minLength={8} preventAutofill describedBy="password-confirmation" />
      </div>
      <div className="password-validation" id="password-requirements">
        <strong>Password requirements</strong>
        <ul>{checks.map(check => <li className={password ? (check.valid ? "valid" : "invalid") : ""} key={check.label}>{check.valid && password ? "✓" : "○"} {check.label}</li>)}</ul>
        <p id="password-confirmation" className={confirmPassword ? (confirmationReady ? "valid" : "invalid") : ""}>
          {confirmPassword ? (confirmationReady ? "✓ Passwords match" : "○ Passwords do not match") : "Confirm the same password."}
        </p>
      </div>
      <p>The new user receives the HR Manager role.</p>
      <div className="actions"><Button type="submit" disabled={!formReady}>Create HR Manager</Button></div>
    </form>}
    {error && <div className="login-error" role="alert">{error}</div>}
    {users.isPending ? <div className="state">Loading workspace users…</div>
      : users.isError ? <div className="state error" role="alert">Unable to load workspace users.</div>
      : <div className="panel table-panel">
        <div className="panel-head">
          <div>
            <h3>Workspace users <span className="count">{users.data.length}</span></h3>
            <p>Accounts have explicit Administrator or HR Manager roles. Your own account is protected.</p>
          </div>
        </div>
        <table>
          <thead><tr><th>User</th><th>Role</th><th>Account status</th><th>Action</th></tr></thead>
          <tbody>{users.data.map(user => <tr key={user.id}>
            <td><b>{user.name}</b><small>@{user.username} · {user.email}</small></td>
            <td><span className={user.role === "ADMIN" ? "role admin" : "role"}>{user.role === "ADMIN" ? "Administrator" : "HR Manager"}</span></td>
            <td><span className={`status ${user.is_active ? "" : "inactive"}`}>{user.is_active ? "Active" : "Inactive"}</span></td>
            <td>{user.id === currentUserId
              ? <span className="self-label">Your account</span>
              : <div className="row-actions">
                <Button variant="ghost" className="small-button" disabled={busyId === user.id} onClick={() => toggle(user)}>{user.is_active ? "Deactivate" : "Activate"}</Button>
                <Button className="small-button" disabled={busyId === user.id || !user.is_active} onClick={() => transfer(user)}>Transfer admin</Button>
              </div>}</td>
          </tr>)}</tbody>
        </table>
      </div>}
  </>;
}
