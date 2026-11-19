import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Button from "../../components/Button";
import { TableState } from "../../components/Table";
import { api, money, type Employee } from "../../shared/api";

export function ProfileDrawer({ id, onClose }: { id: number; onClose: () => void }) {
  const client = useQueryClient();
  const profile = useQuery({ queryKey: ["employee", id], queryFn: () => api<Employee>(`/api/employees/${id}`) });
  const [editing, setEditing] = useState(false);
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const employee = profile.data;
  const startEdit = () => {
    if (!employee) return;
    setAmount(employee.salary.amount);
    setReason("");
    setError("");
    setSaved(false);
    setEditing(true);
  };
  const save = async () => {
    if (!employee || !Number.isFinite(Number(amount)) || Number(amount) <= 0) {
      setError("Enter a salary amount greater than zero.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await api(`/api/employees/${id}`, {
        method: "PATCH",
        body: JSON.stringify({
          amount,
          reason: reason.trim() || "Salary update",
        }),
      });
      await Promise.all([
        client.invalidateQueries({ queryKey: ["employee", id] }),
        client.invalidateQueries({ queryKey: ["employees"] }),
        client.invalidateQueries({ queryKey: ["dashboard"] }),
        client.invalidateQueries({ queryKey: ["compensation-breakdown"] }),
      ]);
      setEditing(false);
      setSaved(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to save salary.");
    } finally {
      setSaving(false);
    }
  };

  return <div className="drawer-backdrop" onClick={onClose}>
    <section className="drawer" role="dialog" aria-modal="true" aria-label="Employee salary profile" onClick={event => event.stopPropagation()}>
      {profile.isPending ? <TableState message="Loading profile…" />
        : profile.isError || !employee ? <TableState message="Unable to load this employee." error />
        : <>
          <div className="drawer-head">
            <div>
              <p className="eyebrow">Employee profile</p>
              <h2>{employee.full_name}</h2>
              <p>{employee.department} · {employee.country}<br />{employee.email}</p>
            </div>
            <button className="close" aria-label="Close profile" onClick={onClose}>×</button>
          </div>
          <div className="profile-grid">
            <div><span>Current salary</span><b>{employee.salary.currency} {Number(employee.salary.amount).toLocaleString()}</b><small>{employee.salary.pay_frequency}</small></div>
            <div><span>USD equivalent</span><b>{money(employee.annualized_usd)}</b><small>Annualized reporting value</small></div>
          </div>
          {editing
            ? <div className="edit-box">
              <h3>Edit salary record</h3>
              <label>Salary amount
                <input value={amount} onChange={event => setAmount(event.target.value)} type="number" min="0.01" step="0.01" />
              </label>
              <label>Reason for change
                <input value={reason} maxLength={200} onChange={event => setReason(event.target.value)} placeholder="e.g. annual review" />
              </label>
              <p>Changes are added to the salary history.</p>
              {error && <p className="state error" role="alert">{error}</p>}
              <div className="actions">
                <Button variant="ghost" onClick={() => setEditing(false)} disabled={saving}>Cancel</Button>
                <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save update"}</Button>
              </div>
            </div>
            : <>
              <div className="callout">Effective since <b>{employee.salary.effective_date}</b>. Salary values are stored in the employee’s local currency.</div>
              <Button onClick={startEdit}>Edit salary record</Button>
              {saved && <div className="success" role="status">Salary updated and audit event recorded.</div>}
            </>}
          <div className="history">
            <h3>Salary history</h3>
            {employee.salary_history?.length
              ? [...employee.salary_history].reverse().map((item, index) => (
                <div className="history-entry" key={`${item.created_at}-${index}`}>
                  <b>{item.reason || "Salary update"}</b>
                  <span>{item.currency} {Number(item.amount).toLocaleString()} · {item.pay_frequency}</span>
                  <small>Effective {item.effective_date}</small>
                </div>
              ))
              : <p>No previous salary changes recorded.</p>}
          </div>
        </>}
    </section>
  </div>;
}
