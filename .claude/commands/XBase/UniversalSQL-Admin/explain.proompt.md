# /explain — SQL Execution Plan Inspector

Show the XBase execution plan for a SQL statement without running it.

Follow the steps in `XBase-UniversalSQL-Admin-Explain`:

1. Accept the SQL statement from `$ARGUMENTS` (or from the user if not provided).
2. Call `XBase-UniversalSQL-Explain` with the SQL and current `ConnectionName` (if any).
3. Display: `Execution Plan for: {SQL}` followed by a table of Step | SQL Clause | XBase Skill | Notes.
4. For any step with no index coverage, append a `⚠` advisory suggesting a `CREATE INDEX`.
5. Display any validation warnings or info issues after the plan.

$ARGUMENTS
