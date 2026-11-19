import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Button from "../../components/Button";
import Card from "../../components/Card";
import { Breakdown, fetchGroups, type GroupBy, type Metric } from "../../components/CompensationCharts";
import { money } from "../../shared/api";

function InsightsCharts() {
  const [groupBy, setGroupBy] = useState<GroupBy>("department");
  const [metric, setMetric] = useState<Metric>("payroll_usd");
  const { data, isPending, isError } = useQuery({ queryKey: ["compensation-breakdown", groupBy], queryFn: () => fetchGroups(groupBy) });
  return <><div className="heading"><div><p className="eyebrow">Compensation intelligence</p><h1>Explore compensation</h1><p>Compare payroll and average pay across the organization.</p></div></div><div className="insight-controls"><div role="group" aria-label="Group by"><Button variant={groupBy === "department" ? "primary" : "ghost"} onClick={() => setGroupBy("department")}>Departments</Button><Button variant={groupBy === "country" ? "primary" : "ghost"} onClick={() => setGroupBy("country")}>Countries</Button></div><div role="group" aria-label="Measure"><Button variant={metric === "payroll_usd" ? "primary" : "ghost"} onClick={() => setMetric("payroll_usd")}>Total payroll</Button><Button variant={metric === "average_salary_usd" ? "primary" : "ghost"} onClick={() => setMetric("average_salary_usd")}>Average salary</Button></div></div><div className="insights-charts"><Breakdown groupBy={groupBy} metric={metric}/><Card className="chart-card insight-table"><div className="chart-card-heading"><div><h3>{groupBy === "department" ? "Department" : "Country"} comparison</h3><p>Annualized values in USD</p></div></div>{isPending ? <p>Loading comparison…</p> : isError ? <p role="alert">Could not load comparison.</p> : <table><thead><tr><th>{groupBy === "department" ? "Department" : "Country"}</th><th>People</th><th>Payroll</th><th>Average</th></tr></thead><tbody>{data?.map(row => <tr key={row.group_name}><td><b>{row.group_name}</b></td><td>{row.headcount.toLocaleString()}</td><td>{money(row.payroll_usd)}</td><td>{money(row.average_salary_usd)}</td></tr>)}</tbody></table>}</Card></div><p className="chart-footnote">The same annualization and fixed FX assumptions are used across dashboard and insights.</p></>;
}

export default function InsightsPage() {
  return <InsightsCharts />;
}
