# XBase-Runtime-Detect

Verify that the AI agent's execution environment supports the abstract file system primitives required by XBase skills, and confirm write access to the intended database root.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| DatabaseRoot | string | yes | The intended path where XBase database directories will be stored |
| VerifyWriteAccess | bool | no (default true) | Perform write and read test operations inside `DatabaseRoot` to confirm the agent can perform file I/O |

## Outputs

```json
{
  "Success": true,
  "EnvironmentReady": true,
  "DatabaseRoot": "/absolute/path/to/databases",
  "CanCreateDirectory": true,
  "CanReadBinaryFile": true,
  "CanWriteBinaryFile": true,
  "CanMoveFileAtomic": true,
  "CanCopyDirectory": true,
  "Issues": [],
  "DetectedAt": "2026-06-27T14:00:00Z"
}
```

## Steps

1. Resolve `DatabaseRoot` to an absolute path. Record this absolute path as the canonical value of `DatabaseRoot` in the output.
2. Check whether `DatabaseRoot` exists using `directory-exists`. If it does not exist, attempt `create-directory(DatabaseRoot)`. Record the outcome in `CanCreateDirectory`. If the directory cannot be created, add "Cannot create database root directory" to `Issues` and return `XBASE_RUNTIME_ROOT_INACCESSIBLE`.
3. If `VerifyWriteAccess` is true: write a small text payload to `{DatabaseRoot}/_xbase_env_check.tmp` using `write-text-file`; read it back using `read-text-file`; then delete the file. If the write operation fails, add "Write access denied on DatabaseRoot" to `Issues`. If the read-back fails after a successful write, add "Read-back failed after write" to `Issues`.
4. Verify binary file capability: write a 4-byte binary payload to `{DatabaseRoot}/_xbase_bin_check.tmp` using `write-binary-file`; read it back using `read-binary-file`; confirm the bytes match the written payload; then delete the file. Record the write result in `CanWriteBinaryFile` and the read result in `CanReadBinaryFile`. If either operation fails, add "Binary file I/O not supported by agent tools" to `Issues`.
5. Verify atomic move capability: write a small text file to `{DatabaseRoot}/_xbase_move_src.tmp`; move it to `{DatabaseRoot}/_xbase_move_dst.tmp` using `move-file-atomic`; confirm the destination file now exists; then delete it. Record the result in `CanMoveFileAtomic`. If the move fails, add "Atomic file move not supported by agent tools" to `Issues`.
6. Verify directory copy capability: create a temporary directory at `{DatabaseRoot}/_xbase_copy_src.tmp/` containing one small file; copy the entire directory to `{DatabaseRoot}/_xbase_copy_dst.tmp/` using `copy-directory-recursive`; confirm the copy exists; then delete both directories. Record the result in `CanCopyDirectory`. If the copy fails, add "Directory copy not supported by agent tools" to `Issues`.
7. Set `EnvironmentReady` to true if `Issues` is empty; set it to false otherwise.
8. Return all capability flags, `Issues`, `DatabaseRoot` (absolute path), and `DetectedAt` set to the current ISO-8601 timestamp.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_RUNTIME_ROOT_INACCESSIBLE` | `DatabaseRoot` cannot be created or written — the agent lacks access to the target path |
| `XBASE_RUNTIME_BINARY_IO_FAILED` | The agent's tools do not support binary file read/write, which is required for all DBF and NDX operations |

## Dependencies

- Writable local file system accessible to the AI agent's tools
- No other XBase skills are required; this skill may be called before any database exists
