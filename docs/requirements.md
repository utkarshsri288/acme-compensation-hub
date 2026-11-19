# ACME Compensation Hub — One-page requirements

## Goal and user

Replace HR spreadsheets with a searchable salary workspace for 10,000 ACME employees across six countries. The HR Manager finds people, updates base salary, and compares pay by country or department. An Administrator manages HR access.

## MVP scope

- **Access:** username/password login and API-enforced Administrator/HR Manager roles. Administrators create, activate, deactivate, and transfer access; HR Managers use compensation features.
- **Directory:** SQL-backed name/email search, country/department/status filters, sorting, 12-row pagination, and salary profiles.
- **Salary management:** show local amount, pay frequency, effective date, annualized USD, and history. HR edits the amount with a reason; the API validates it and atomically records before/after values.
- **Pay questions:** dashboard shows headcount, annualized USD payroll, average salary, and country count. Insights group headcount, payroll, and average by country or department using documented fixed FX rates.
- **Export and data:** CSV download of the filtered/sorted **current page**; deterministic SQLite seed of exactly 10,000 synthetic employees and salary records.
- **Quality:** responsive React UI, Django API, repeatable local setup, and automated core-flow tests.

## Deliberate exclusions and reasons

- **New employee creation, bulk import, approvals:** duplicate detection and review workflows add complexity; seeded employees support the single-record MVP.
- **Payroll execution, tax, benefits, bonus, equity:** regional rules and external systems exceed base salary management.
- **Selectable reporting currency and live FX:** fixed USD rates keep demo comparisons reproducible; Finance must approve rates before real use.
- **Enterprise SSO and real employee data:** local demo authentication and synthetic data avoid premature identity/privacy assumptions.

## Acceptance checks

HR can find and update an employee, see history, compare pay, and export a page. Admin can create users and transfer ownership without self-editing. Fresh migration and seed produce 10,000 employees and 10,000 salaries.
