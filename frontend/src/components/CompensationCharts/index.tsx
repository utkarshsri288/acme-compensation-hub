import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Card from "../Card";
import "./styles.css";

type Group = { group_name: string; headcount: number; payroll_usd: number; average_salary_usd: number };
export type GroupBy = "department" | "country";
export type Metric = "payroll_usd" | "average_salary_usd";
const palette = ["#2b66c9", "#4dd8ee", "#1fa39a", "#e0972b", "#8b8fae", "#6d4aff", "#d8324c"];
const currency = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
const compact = (value: number) => new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);

export async function fetchGroups(groupBy: GroupBy): Promise<Group[]> {
  const token = localStorage.getItem("acme_token");
  const response = await fetch(`/api/insights?group_by=${groupBy}`, { headers: { Authorization: `Token ${token ?? ""}` } });
  if (!response.ok) throw new Error("Could not load compensation breakdown.");
  return response.json();
}

export function Breakdown({ groupBy, metric = "payroll_usd" }: { groupBy: GroupBy; metric?: Metric }) {
  const { data, isPending, isError } = useQuery({ queryKey: ["compensation-breakdown", groupBy], queryFn: () => fetchGroups(groupBy) });
  const title = groupBy === "department" ? "Payroll by department" : "Payroll by country";
  return <Card className="chart-card"><div className="chart-card-heading"><div><h3>{title}</h3><p>Annualized USD · {metric === "payroll_usd" ? "total payroll" : "average salary"}</p></div><span className="chart-unit">USD</span></div>{isPending ? <p className="chart-message">Loading breakdown…</p> : isError ? <p className="chart-message" role="alert">Could not load chart.</p> : !data?.length ? <p className="chart-message">No compensation data yet.</p> : <div className="chart-canvas" role="img" aria-label={`${title}, ${metric === "payroll_usd" ? "total payroll" : "average salary"}`}><ResponsiveContainer width="100%" height="100%"><BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 12 }}><CartesianGrid stroke="#e3e5f2" strokeDasharray="3 4" horizontal={false}/><XAxis type="number" tickFormatter={compact} tick={{ fill: "#686c89", fontSize: 11 }} axisLine={false} tickLine={false}/><YAxis type="category" dataKey="group_name" width={116} tick={{ fill: "#585c78", fontSize: 11 }} axisLine={false} tickLine={false}/><Tooltip formatter={(value: number) => currency(value)} cursor={{ fill: "#eef3ff" }}/><Bar dataKey={metric} name={metric === "payroll_usd" ? "Payroll" : "Average salary"} fill="#2b66c9" radius={[0, 5, 5, 0]} maxBarSize={22}/></BarChart></ResponsiveContainer></div>}</Card>;
}

export function CountryShare() {
  const { data, isPending, isError } = useQuery({ queryKey: ["compensation-breakdown", "country"], queryFn: () => fetchGroups("country") });
  return <Card className="chart-card"><div className="chart-card-heading"><div><h3>Payroll share by country</h3><p>Portion of annualized USD payroll</p></div></div>{isPending ? <p className="chart-message">Loading breakdown…</p> : isError ? <p className="chart-message" role="alert">Could not load chart.</p> : !data?.length ? <p className="chart-message">No compensation data yet.</p> : <><div className="share-chart" role="img" aria-label="Payroll share by country"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="payroll_usd" nameKey="group_name" innerRadius={68} outerRadius={100} paddingAngle={2} stroke="none">{data.map((item, index) => <Cell key={item.group_name} fill={palette[index % palette.length]}/>)}</Pie><Tooltip formatter={(value: number) => currency(value)}/></PieChart></ResponsiveContainer></div><div className="share-legend">{data.map((item, index) => <div key={item.group_name}><i style={{ background: palette[index % palette.length] }}/><span>{item.group_name}</span><b>{Math.round(item.payroll_usd / data.reduce((sum, row) => sum + row.payroll_usd, 0) * 100)}%</b></div>)}</div></>}</Card>;
}

export function MetricCard({ label, value, hint }: { label: string; value: string; hint: string }) { return <Card className="chart-metric"><span>{label}</span><strong>{value}</strong><small>{hint}</small></Card>; }
