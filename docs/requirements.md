# ACME Salary Management — Product Requirements

## Goal

Give ACME HR managers a trustworthy, fast way to manage employee compensation and answer common pay questions without maintaining spreadsheets. The MVP must feel comfortable at 10,000 employees and make every change explainable.

## Primary user

An HR manager who needs to find an employee, review or update salary data, understand compensation by country/department, and export a working set for follow-up.

## In scope (MVP)

- Employee directory with server-side search, pagination, and filters for country, department, employment status, and compensation band.
- Employee salary profile with base salary, currency, pay frequency, effective date, employment details, and last updated metadata.
- Create and edit salary records with validation; preserve an audit event for each change.
- Dashboard summary cards: headcount, total annualized payroll in a selected reporting currency, average salary, and countries represented.
- Compensation analysis grouped by country and department with headcount, average, minimum, maximum, and total annualized pay.
- CSV export of the currently filtered employee list.
- Deterministic seed script generating exactly 10,000 realistic employees across countries and departments.
- Responsive web UI, documented API, automated tests, and a simple local/deployment path.

## Product principles

1. **Safe by default:** money values are validated, edits are explicit, and audit history is append-only.
2. **Useful at a glance:** the dashboard answers “how do we pay people?” before asking the manager to build a report.
3. **Fast for 10,000 rows:** never send the entire directory to the browser for routine browsing; aggregate in the database.
4. **Transparent assumptions:** reporting currency and annualization rules are visible in the UI.

## Deliberately out of scope

- Authentication/SSO and role-based access: essential for production, but not needed to demonstrate the core workflow; the service boundary leaves room for it.
- Payroll execution, tax calculations, benefits, bonuses, equity, and local legal compliance: these require country-specific rules and integrations beyond a salary-management MVP.
- Multi-currency FX history: the MVP stores local currency and uses a documented static rate table for comparable dashboard totals; a provider-backed rate service can replace it later.
- Bulk upload/import and approval workflows: useful next steps, but they add conflict resolution and permission complexity before the single-record workflow is proven.
- Real-time collaboration, notifications, and mobile-native apps: not required for the stated HR-manager workflow.

## Success measures

- A manager can find and update a record in under 30 seconds.
- Directory queries return within 300 ms locally for common filters at 10,000 rows.
- Summary and analysis numbers reconcile with the same salary records visible in the directory.
- Core domain/API behavior is covered by fast deterministic tests.

## Open risks / follow-ups

- Confirm the canonical source of FX rates and effective-date policy with Finance.
- Add SSO, authorization, encryption, retention, and audit export before handling real employee data.
- Validate local currency and salary-band rules with regional HR partners.
