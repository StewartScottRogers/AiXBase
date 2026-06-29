# XBase-UniversalSQL-Admin-Schema

Read the XBase `_schema.json` for a database and emit equivalent `CREATE TABLE` SQL DDL for all or specified tables. Useful for documentation, cross-database migration, and understanding the schema in familiar SQL syntax.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | no | Active connection alias; if omitted, `DatabaseName` is required |
| `DatabaseName` | string | no | Database name to connect to if no `ConnectionName` is open |
| `Tables` | array | no | Subset of table names to include; omit to include all tables |

## Outputs

```sql
-- XBase Schema: inventory
-- Generated: 2026-06-29T15:50:00Z

CREATE TABLE IF NOT EXISTS Products (
    Id        INTEGER  NOT NULL  PRIMARY KEY,
    SKU       TEXT     NOT NULL  UNIQUE,
    Label     TEXT     NOT NULL,
    Price     REAL,
    IsActive  INTEGER  NOT NULL  DEFAULT 1,
    CreatedAt TEXT,
    UpdatedAt TEXT,
    IsDeleted INTEGER  NOT NULL  DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Orders (
    Id         INTEGER  NOT NULL  PRIMARY KEY,
    ProductId  INTEGER  NOT NULL  REFERENCES Products(Id),
    Quantity   INTEGER  NOT NULL,
    OrderedAt  TEXT,
    CreatedAt  TEXT,
    UpdatedAt  TEXT,
    IsDeleted  INTEGER  NOT NULL  DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_orders_product ON Orders (ProductId);
```

## Steps

1. If `ConnectionName` is not supplied, call `XBase-Database-Connect` with `DatabaseName` to establish a temporary connection.
2. Call `XBase-Schema-TableList` with `ConnectionName` to obtain all table names. If `Tables` is supplied, filter to that subset; return an error for any requested table not found in the schema.
3. For each table (in schema order):
   a. Call `XBase-Schema-ColumnList` with `ConnectionName` and `TableName`.
   b. Emit `CREATE TABLE IF NOT EXISTS {TableName} (` followed by one column definition per line:
      - `{Name}  {SQLType}` where `SQLType` maps from XBase type: `INTEGER` → `INTEGER`, `TEXT` → `TEXT`, `REAL` → `REAL`.
      - Append `NOT NULL` if `Nullable: false`.
      - Append `PRIMARY KEY` if `PrimaryKey: true`.
      - Append `UNIQUE` if `Unique: true`.
      - Append `DEFAULT {value}` if `Default` is non-null.
      - Append `REFERENCES {ForeignKey}` if a `ForeignKey` annotation is present.
   c. Close with `);` and a blank line.
4. Call `XBase-Index-List` with `ConnectionName`; for each index emit: `CREATE INDEX IF NOT EXISTS {name} ON {table} ({columns});`.
5. Prepend a comment header: `-- XBase Schema: {DatabaseName or ConnectionName}\n-- Generated: {current ISO-8601 timestamp}`.
6. Display the full DDL in a fenced `sql` code block.
7. If a temporary connection was opened in step 1, call `XBase-Database-Disconnect`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_DATABASE_NOT_FOUND` | `DatabaseName` does not resolve to a valid database |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | A requested table name from `Tables` is not in the schema |

## Dependencies

- `XBase-Database-Connect` — when no `ConnectionName` is open
- `XBase-Database-Disconnect` — temporary connection teardown
- `XBase-Schema-TableList` — enumerate tables
- `XBase-Schema-ColumnList` — column definitions per table
- `XBase-Index-List` — index definitions
