import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Button from "../../components/Button";
import DataTable, { Pagination, TableState } from "../../components/Table";
import EmployeeExport from "../../components/EmployeeExport";
import { api, money, type ListResponse } from "../../shared/api";
export { ProfileDrawer } from "./ProfileDrawer";

export type DirectoryProps = {
  search: string;
  setSearch: (value: string) => void;
  country: string;
  setCountry: (value: string) => void;
  department: string;
  setDepartment: (value: string) => void;
  status: string;
  setStatus: (value: string) => void;
  page: number;
  setPage: (value: number) => void;
  sort: string;
  direction: "asc" | "desc";
  onSort: (column: string) => void;
  onSelect: (id: number) => void;
};

const departments = ["Engineering", "People", "Finance", "Sales", "Marketing", "Operations", "Legal"];
const countries = ["United States", "India", "United Kingdom", "Germany", "Singapore", "Australia"];
const pageSize = 12;

export default function EmployeesPage(props: DirectoryProps) {
  const { search, country, department, status, page, sort, direction } = props;
  const [searchDraft, setSearchDraft] = useState(search);
  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (searchDraft !== search) props.setSearch(searchDraft);
    }, 300);
    return () => window.clearTimeout(timer);
  }, [searchDraft, search, props.setSearch]);

  const params = new URLSearchParams({
    search, country, department, status, page: String(page), page_size: String(pageSize), sort, direction,
  });
  const employees = useQuery({
    queryKey: ["employees", search, country, department, status, page, sort, direction],
    queryFn: () => api<ListResponse>(`/api/employees?${params}`),
  });

  const sortHeader = (label: string, column: string) => (
    <Button className="sort-button" onClick={() => props.onSort(column)}
      aria-label={`Sort by ${label}`}>
      {label} {sort === column ? (direction === "asc" ? "↑" : "↓") : "↕"}
    </Button>
  );
  const total = employees.data?.meta.total ?? 0;
  const hasFilters = Boolean(searchDraft || country || department || status);

  return <>
    <div className="heading">
      <div>
        <p className="eyebrow">People & compensation</p>
        <h1>Employee directory</h1>
        <p>Search, filter, sort, and open a salary profile.</p>
      </div>
      <EmployeeExport page={page} sort={sort} direction={direction} search={search} country={country} department={department} status={status} />
    </div>
    <div className="filters">
      <input aria-label="Search employees" placeholder="⌕  Search name or email" value={searchDraft} onChange={event => setSearchDraft(event.target.value)} />
      <select aria-label="Country" value={country} onChange={event => props.setCountry(event.target.value)}>
        <option value="">All countries</option>
        {countries.map(value => <option key={value}>{value}</option>)}
      </select>
      <select aria-label="Department" value={department} onChange={event => props.setDepartment(event.target.value)}>
        <option value="">All departments</option>
        {departments.map(value => <option key={value}>{value}</option>)}
      </select>
      <select aria-label="Status" value={status} onChange={event => props.setStatus(event.target.value)}>
        <option value="">All statuses</option>
        <option value="active">Active</option>
        <option value="on_leave">On leave</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
    {employees.isPending ? <TableState message="Loading employees…" />
      : employees.isError ? <TableState message="Unable to load employee records. Please try again." error />
      : <DataTable className="employee-directory-table">
        <div className="panel-head">
          <div>
            <h3>All employees <span className="count">{total.toLocaleString()}</span></h3>
            <p>{total ? `Showing ${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, total)}` : "No employees found"}</p>
          </div>
          {total > 0 && <span className="page-label">Page {employees.data.meta.page} of {employees.data.meta.pages}</span>}
        </div>
        {total === 0
          ? <div className="directory-empty">
            <p>{hasFilters ? "No employees match these filters." : "No employees are available yet."}</p>
            {hasFilters && <Button variant="ghost" onClick={() => {
              setSearchDraft("");
              props.setSearch("");
              props.setCountry("");
              props.setDepartment("");
              props.setStatus("");
            }}>Clear filters</Button>}
          </div>
          : <div className="employee-table-scroll">
            <table>
              <thead><tr>
                <th>{sortHeader("Employee", "name")}</th>
                <th>{sortHeader("Department", "department")}</th>
                <th>{sortHeader("Country", "country")}</th>
                <th>{sortHeader("Annual salary", "salary")}</th>
                <th>{sortHeader("Status", "status")}</th>
              </tr></thead>
              <tbody>{employees.data.data.map(employee => (
                <tr className="clickable" key={employee.id} onClick={() => props.onSelect(employee.id)} tabIndex={0}
                  onKeyDown={event => { if (event.key === "Enter") props.onSelect(employee.id); }}>
                  <td><b>{employee.full_name}</b><small>{employee.email}</small></td>
                  <td>{employee.department}</td>
                  <td>{employee.country}</td>
                  <td>{money(employee.annualized_usd)}</td>
                  <td><span className="status">{employee.status.replace("_", " ")}</span></td>
                </tr>
              ))}</tbody>
            </table>
          </div>}
        <Pagination page={page} pages={employees.data.meta.pages} onPageChange={props.setPage} />
      </DataTable>}
  </>;
}
