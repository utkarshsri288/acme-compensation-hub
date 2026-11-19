export type Dashboard = { headcount: number; payroll_usd: number; average_salary_usd: number; countries: number };
export type SalaryHistory = { amount: string; currency: string; pay_frequency: string; effective_date: string; reason: string; created_at: string };
export type Employee = { id: number; full_name: string; first_name: string; last_name: string; email: string; country: string; department: string; status: string; annualized_usd: number; salary: { amount: string; currency: string; pay_frequency: string; effective_date: string }; salary_history?: SalaryHistory[] };
export type ListResponse = { data: Employee[]; meta: { total: number; page: number; pages: number } };
export type WorkspaceRole = "ADMIN" | "HR_MANAGER";
export type AuthUser = { id: number; username: string; name: string; email: string; role: WorkspaceRole };
export type AdminUser = AuthUser & { is_active: boolean };

export const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

export async function api<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("acme_token");
  const response = await fetch(url, { headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Token ${token}` } : {}) }, ...options });
  if (!response.ok) throw new Error((await response.json()).detail || "Something went wrong");
  return response.status === 204 ? (undefined as T) : response.json();
}
