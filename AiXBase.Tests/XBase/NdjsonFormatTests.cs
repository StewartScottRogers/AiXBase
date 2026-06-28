using System.Text;
using System.Text.Json;
using AiXBase.Tests.Helpers;
using Xunit;

namespace AiXBase.Tests.XBase;

/// <summary>
/// Integration tests that validate the NDJSON-over-DBF format of the AiXBaseTracking database.
/// These tests hit real files on disk — no mocking.
/// </summary>
public class NdjsonFormatTests
{
    private static readonly string DbRoot =
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "AiXBaseTracking", "tracking"));

    [Fact]
    public void DatabaseRoot_Exists()
        => Assert.True(Directory.Exists(DbRoot), $"Database root not found: {DbRoot}");

    [Fact]
    public void MetaJson_IsValidJson()
    {
        var path = Path.Combine(DbRoot, "_meta.json");
        Assert.True(File.Exists(path));
        var doc = JsonDocument.Parse(File.ReadAllText(path, Encoding.UTF8));
        Assert.True(doc.RootElement.TryGetProperty("Name", out _), "_meta.json missing Name");
        Assert.True(doc.RootElement.TryGetProperty("XBaseVersion", out _), "_meta.json missing XBaseVersion");
    }

    [Fact]
    public void SchemaJson_HasExpectedTables()
    {
        var path = Path.Combine(DbRoot, "_schema.json");
        Assert.True(File.Exists(path));
        var doc = JsonDocument.Parse(File.ReadAllText(path, Encoding.UTF8));
        var tables = doc.RootElement.GetProperty("Tables").EnumerateArray()
            .Select(t => t.GetProperty("Name").GetString())
            .ToHashSet();

        string[] expected =
        [
            "Users", "Sessions", "Statuses", "StatusTransitions", "Priorities",
            "Categories", "Tags", "Tickets", "Comments", "Attachments",
            "TicketHistory", "TicketTags"
        ];
        foreach (var name in expected)
            Assert.Contains(name, tables);
    }

    [Theory]
    [InlineData("Users.dbf")]
    [InlineData("Sessions.dbf")]
    [InlineData("Statuses.dbf")]
    [InlineData("StatusTransitions.dbf")]
    [InlineData("Priorities.dbf")]
    [InlineData("Categories.dbf")]
    [InlineData("Tags.dbf")]
    [InlineData("Tickets.dbf")]
    [InlineData("Comments.dbf")]
    [InlineData("Attachments.dbf")]
    [InlineData("TicketHistory.dbf")]
    [InlineData("TicketTags.dbf")]
    public void DbfFile_HasUtf8Bom(string fileName)
    {
        var path = Path.Combine(DbRoot, fileName);
        Assert.True(File.Exists(path), $"Missing: {fileName}");
        var bytes = File.ReadAllBytes(path);
        Assert.True(bytes.Length >= 3, $"{fileName} is too short to contain BOM");
        Assert.Equal(0xEF, bytes[0]);
        Assert.Equal(0xBB, bytes[1]);
        Assert.Equal(0xBF, bytes[2]);
    }

    [Theory]
    [InlineData("Users.dbf")]
    [InlineData("Statuses.dbf")]
    [InlineData("Tickets.dbf")]
    [InlineData("TicketHistory.dbf")]
    public void DbfFile_AllDataLinesAreValidJson(string fileName)
    {
        var path = Path.Combine(DbRoot, fileName);
        var text = File.ReadAllText(path, Encoding.UTF8);
        foreach (var line in text.Split("\r\n", StringSplitOptions.RemoveEmptyEntries))
        {
            var trimmed = line.Trim();
            if (!trimmed.StartsWith('{')) continue;
            var ex = Record.Exception(() => JsonDocument.Parse(trimmed));
            Assert.Null(ex);
        }
    }

    [Fact]
    public void Statuses_HasSixExpectedStatuses()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Statuses.dbf"));
        Assert.Equal(6, records.Count);
        var names = records.Select(r => DbfHelper.GetString(r, "Name")).ToHashSet();
        Assert.Contains("Backlog", names);
        Assert.Contains("In Progress", names);
        Assert.Contains("In Review", names);
        Assert.Contains("Blocked", names);
        Assert.Contains("Done", names);
        Assert.Contains("Cancelled", names);
    }

    [Fact]
    public void Statuses_BacklogIsDefault()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Statuses.dbf"));
        var backlog = records.Single(r => DbfHelper.GetString(r, "Name") == "Backlog");
        Assert.Equal(1, DbfHelper.GetInt(backlog, "IsDefault"));
    }

    [Fact]
    public void Statuses_DoneAndCancelledAreTerminal()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Statuses.dbf"));
        var terminal = records
            .Where(r => DbfHelper.GetInt(r, "IsTerminal") == 1)
            .Select(r => DbfHelper.GetString(r, "Name"))
            .ToHashSet();
        Assert.Contains("Done", terminal);
        Assert.Contains("Cancelled", terminal);
    }

    [Fact]
    public void Priorities_HasFourExpectedPriorities()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Priorities.dbf"));
        Assert.Equal(4, records.Count);
        var names = records.Select(r => DbfHelper.GetString(r, "Name")).ToHashSet();
        foreach (var p in new[] { "Critical", "High", "Medium", "Low" })
            Assert.Contains(p, names);
    }

    [Fact]
    public void Users_HasAdminUser()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Users.dbf"));
        var srogers = records.SingleOrDefault(r => DbfHelper.GetString(r, "Username") == "srogers");
        Assert.NotEqual(default, srogers);
        Assert.Equal(1, DbfHelper.GetInt(srogers, "IsAdmin"));
        Assert.Equal(1, DbfHelper.GetInt(srogers, "IsActive"));
    }

    [Fact]
    public void Tickets_HasNineTickets()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Tickets.dbf"));
        Assert.Equal(9, records.Count);
    }

    [Fact]
    public void Tickets_TicketNumbersAreSequential()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "Tickets.dbf"));
        var numbers = records
            .Select(r => DbfHelper.GetString(r, "TicketNumber"))
            .OrderBy(n => n)
            .ToList();
        for (int i = 0; i < numbers.Count; i++)
            Assert.Equal($"TKT-{(i + 1):D4}", numbers[i]);
    }

    [Fact]
    public void StatusTransitions_HasNineEntries()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "StatusTransitions.dbf"));
        Assert.Equal(9, records.Count);
    }

    [Fact]
    public void StatusTransitions_BacklogCanGoToInProgressOrCancelled()
    {
        var records = DbfHelper.ReadLiveRecords(Path.Combine(DbRoot, "StatusTransitions.dbf"));
        // StatusId 1=Backlog, 2=InProgress, 6=Cancelled
        var fromBacklog = records
            .Where(r => DbfHelper.GetInt(r, "FromStatusId") == 1)
            .Select(r => DbfHelper.GetInt(r, "ToStatusId"))
            .ToHashSet();
        Assert.Contains(2, fromBacklog);
        Assert.Contains(6, fromBacklog);
    }

    [Fact]
    public void NdxFiles_HaveUtf8Bom()
    {
        string[] ndxFiles = ["Tickets.idx_TicketNumber.ndx", "Tickets.idx_StatusId.ndx", "Tickets.idx_AssignedToUserId.ndx"];
        foreach (var name in ndxFiles)
        {
            var path = Path.Combine(DbRoot, name);
            Assert.True(File.Exists(path), $"Missing: {name}");
            var bytes = File.ReadAllBytes(path);
            Assert.True(bytes.Length >= 3, $"{name} too short for BOM");
            Assert.Equal(0xEF, bytes[0]);
            Assert.Equal(0xBB, bytes[1]);
            Assert.Equal(0xBF, bytes[2]);
        }
    }
}
