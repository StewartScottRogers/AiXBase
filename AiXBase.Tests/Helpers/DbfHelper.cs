using System.Text;
using System.Text.Json;

namespace AiXBase.Tests.Helpers;

/// <summary>
/// Reads the NDJSON-over-DBF format used by XBase.
/// Each .dbf file is UTF-8 BOM + CRLF blank line + one JSON object per record per CRLF-terminated line.
/// Soft-deleted records have IsDeleted=1 and are included unless filtered.
/// </summary>
internal static class DbfHelper
{
    /// <summary>
    /// Returns all live (non-deleted) records from a .dbf file as JSON elements.
    /// </summary>
    internal static List<JsonElement> ReadLiveRecords(string dbfPath)
        => ReadRecords(dbfPath, includeDeleted: false);

    /// <summary>
    /// Returns all records (including soft-deleted) from a .dbf file.
    /// </summary>
    internal static List<JsonElement> ReadAllRecords(string dbfPath)
        => ReadRecords(dbfPath, includeDeleted: true);

    private static List<JsonElement> ReadRecords(string dbfPath, bool includeDeleted)
    {
        var text = File.ReadAllText(dbfPath, Encoding.UTF8);
        var records = new List<JsonElement>();
        foreach (var line in text.Split("\r\n", StringSplitOptions.RemoveEmptyEntries))
        {
            var trimmed = line.Trim();
            if (!trimmed.StartsWith('{')) continue;
            var doc = JsonDocument.Parse(trimmed);
            if (!includeDeleted
                && doc.RootElement.TryGetProperty("IsDeleted", out var del)
                && del.GetInt32() != 0)
                continue;
            records.Add(doc.RootElement.Clone());
        }
        return records;
    }

    /// <summary>
    /// Returns the string value of a field from a record, or null if absent.
    /// </summary>
    internal static string? GetString(JsonElement record, string field)
        => record.TryGetProperty(field, out var v) ? v.GetString() : null;

    /// <summary>
    /// Returns the int value of a field from a record, or null if absent.
    /// </summary>
    internal static int? GetInt(JsonElement record, string field)
        => record.TryGetProperty(field, out var v) ? v.GetInt32() : null;
}
