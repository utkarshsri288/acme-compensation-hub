# AI-assisted development record

AI coding tools helped turn the ACME HR persona and spreadsheet problem into a bounded MVP, draft the product plan, implement Django/React slices, refactor pages and components, and review UI and backend behavior. Human direction changed the work repeatedly: use username login, define explicit roles, prevent browser autofill in the new-user form, add live password checks, and keep the directory within a fixed viewport.

## Decisions checked against evidence

- **10,000 employees:** use SQL pagination and aggregation rather than fetch every row. Verify the actual database count and add a fresh-database seed check.
- **Cross-country pay:** store local salaries and compare annualized USD using one documented fixed FX table. Test mixed currencies and frequencies in salary sorting.
- **Access:** keep two explicit Django Group roles (`ADMIN`, `HR_MANAGER`) and enforce them in API permission classes, not only in hidden UI controls. Test role transfer and unauthorized access.
- **Salary edits:** write current salary, history, and audit event in one transaction. Test invalid/no-op edits and history output.
- **UI behavior:** use browser inspection to reproduce autofill and styling issues, then verify blank new-user fields, password toggle, validation checklist, and enabled/disabled submit states.

## Verification and limits

Run `python backend/manage.py test compensation`, `npm test --prefix frontend`, `npm run build --prefix frontend`, Django checks, and a local API/UI smoke check. The tests are deterministic and use a separate test database. AI suggestions are reviewed against code and running behavior; generated prose is reconciled with the implemented API. Current limits are recorded in the requirements and architecture notes. No real employee data is used.
