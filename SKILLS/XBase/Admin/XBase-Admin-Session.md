# XBase-Admin-Session

Run an interactive guided admin session for a connected XBase database. Presents a text menu in the conversation, accepts a selection, executes the corresponding Admin skill, displays the result, and loops until the user exits. No file I/O occurs in this skill directly — all operations delegate to the underlying Admin skills.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active connection alias for the database to administer |

## Outputs

The skill produces no structured JSON output. All interaction is conversational: menus are rendered as markdown, results are displayed inline, and the session ends when the user selects Exit or types `q` / `quit` / `exit`.

## Steps

1. Validate `ConnectionName` is registered in the current session; if not, return `XBASE_CONNECTION_INVALID`.
2. Display the main menu:

   ```
   ═══════════════════════════════════════
    XBase Admin  ·  <ConnectionName>
   ═══════════════════════════════════════
    1  Inspect     — health check & counts
    2  Maintain    — pack, rebuild, verify
    3  Execute     — run any XBase skill
    4  Exit
   ═══════════════════════════════════════
   Select [1-4]:
   ```

3. Wait for user input. Normalize the input: strip whitespace, map `q`/`quit`/`exit` to `4`.
4. Dispatch on the selection:

   **Selection 1 — Inspect:**
   a. Display a sub-menu asking which sections to include:
      ```
       Include record counts?  [Y/n]
       Include index info?     [Y/n]
       Include transactions?   [Y/n]
      ```
   b. Call `XBase-Admin-Inspect` with `ConnectionName` and the chosen flags.
   c. Render the result as a markdown table:
      - One row per table: Name, RecordCount, DeletedCount, IndexCount.
      - List `ActiveTransactions` if any are present.
      - If `Anomalies` is non-empty, display each anomaly as a warning line prefixed with `⚠`.
   d. Return to the main menu (step 2).

   **Selection 2 — Maintain:**
   a. Display a sub-menu:
      ```
       Pack soft-deleted records?  [Y/n]  (default Y)
       Rebuild indexes?            [Y/n]  (default Y)
       Verify backups?             [y/N]  (default N)
       Dry run only?               [y/N]  (default N)
      ```
   b. Call `XBase-Admin-Maintain` with `ConnectionName` and the chosen flags.
   c. Display the result: TablesPackaged, IndexesRebuilt, BackupsVerified, any Issues.
   d. Return to the main menu (step 2).

   **Selection 3 — Execute:**
   a. Prompt: `Skill name:` — accept any string.
   b. Prompt: `Inputs (JSON object, or press Enter for {}):` — accept a JSON object string; default to `{}` on empty input.
   c. Parse the Inputs JSON; if malformed, display an error and re-prompt (up to 3 attempts); if still malformed after 3 attempts, return to the main menu.
   d. Call `XBase-Admin-Execute` with `SkillName`, `Inputs`, and `ConnectionName`.
   e. Display the full `Result` object as formatted JSON.
   f. Return to the main menu (step 2).

   **Selection 4 — Exit:**
   a. Display `Session ended.` and return.

   **Unrecognized input:**
   a. Display `Unrecognized selection. Please enter 1, 2, 3, or 4.` and re-display the menu (step 2).

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the current session |

## Dependencies

- `XBase-Admin-Inspect`
- `XBase-Admin-Maintain`
- `XBase-Admin-Execute`
