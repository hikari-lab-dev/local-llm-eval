namespace CsvParser.Tests;

public class CsvLineParserTests
{
    [Fact]
    public void ParsesUnquotedFields()
    {
        Assert.Equal(["a", "b", "c"], CsvLineParser.ParseLine("a,b,c"));
    }

    [Fact]
    public void ParsesQuotedFieldContainingComma()
    {
        Assert.Equal(["a,b", "c"], CsvLineParser.ParseLine("\"a,b\",c"));
    }

    [Fact]
    public void ParsesSingleField()
    {
        Assert.Equal(["only"], CsvLineParser.ParseLine("only"));
    }
}
