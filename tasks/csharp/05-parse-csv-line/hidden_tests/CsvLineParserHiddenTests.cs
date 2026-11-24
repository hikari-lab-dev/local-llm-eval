namespace CsvParser.HiddenTests;

public class CsvLineParserHiddenTests
{
    [Fact]
    public void ParsesEscapedQuoteInsideQuotedField()
    {
        Assert.Equal(["a\"b", "c"], CsvLineParser.ParseLine("\"a\"\"b\",c"));
    }

    [Fact]
    public void ParsesEmptyTrailingField()
    {
        Assert.Equal(["a", "b", ""], CsvLineParser.ParseLine("a,b,"));
    }

    [Fact]
    public void ParsesEmptyLeadingField()
    {
        Assert.Equal(["", "a"], CsvLineParser.ParseLine(",a"));
    }

    [Fact]
    public void ParsesEmptyLine()
    {
        Assert.Equal([""], CsvLineParser.ParseLine(""));
    }

    [Fact]
    public void ParsesQuotedEmptyField()
    {
        Assert.Equal(["", "b"], CsvLineParser.ParseLine("\"\",b"));
    }

    [Fact]
    public void ParsesMultipleQuotedFields()
    {
        Assert.Equal(["a,1", "b,2"], CsvLineParser.ParseLine("\"a,1\",\"b,2\""));
    }
}
