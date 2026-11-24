using System.Text.RegularExpressions;

namespace ShippingFee.HiddenTests;

public class ShippingCalculatorStructureHiddenTests
{
    private static string ReadSourceFile()
    {
        var hiddenTestsDir = Path.GetFullPath(
            Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", ".."));
        var sourceFilePath = Path.Combine(
            hiddenTestsDir, "..", "ShippingFee", "ShippingCalculator.cs");
        return File.ReadAllText(sourceFilePath);
    }

    [Fact]
    public void SourceDoesNotContainElseBlocks()
    {
        var source = ReadSourceFile();

        Assert.DoesNotMatch(new Regex(@"^\s*else\b", RegexOptions.Multiline), source);
    }

    [Fact]
    public void SourceIsSplitIntoAtLeastFourMethods()
    {
        var source = ReadSourceFile();

        var methodCount = new Regex(@"(public|private|internal)\s+static\s+\S+\s+\w+\s*\(")
            .Matches(source).Count;
        Assert.True(methodCount >= 4, $"methodCount={methodCount}");
    }
}
