import { useQuery } from "@tanstack/react-query";
import { api, money, type Dashboard } from "../../shared/api";
import Button from "../../components/Button";
import Card from "../../components/Card";
import { Breakdown, CountryShare, MetricCard } from "../../components/CompensationCharts";

function DashboardCharts({ summary, isLoading, isError, onViewEmployees, name }: { summary?: Dashboard; isLoading: boolean; isError: boolean; onViewEmployees: () => void; name: string }) {
  return <><div className="heading"><div><p className="eyebrow">Compensation overview</p><h1>Good morning, {name.split(" ")[0]}</h1><p>Explore how ACME pays its global workforce.</p></div><Button onClick={onViewEmployees}>Open employee directory →</Button></div>{isLoading ? <Card>Loading compensation overview…</Card> : isError || !summary ? <Card>Unable to load dashboard. Check that the API is running.</Card> : <><div className="chart-metrics"><MetricCard label="Employees" value={summary.headcount.toLocaleString()} hint="Total records"/><MetricCard label="Annual payroll" value={money(summary.payroll_usd)} hint="USD equivalent"/><MetricCard label="Average salary" value={money(summary.average_salary_usd)} hint="Annualized USD"/><MetricCard label="Countries" value={String(summary.countries)} hint="Represented"/></div><div className="dashboard-charts"><Breakdown groupBy="department"/><CountryShare/></div><p className="chart-footnote">Comparisons use the assessment’s fixed FX rates. Original salaries remain in local currency.</p></>}</>;
}


export default function DashboardPage({ name, onViewEmployees }: { name: string; onViewEmployees: () => void }) {
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: () => api<Dashboard>("/api/dashboard") });
  return <DashboardCharts summary={dashboard.data} isLoading={dashboard.isLoading} isError={dashboard.isError} onViewEmployees={onViewEmployees} name={name} />;
}
