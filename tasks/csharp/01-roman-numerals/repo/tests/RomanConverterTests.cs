namespace RomanNumerals.Tests;

public class RomanConverterTests
{
    [Fact]
    public void ConvertsOne()
    {
        Assert.Equal("I", RomanConverter.ToRoman(1));
    }

    [Fact]
    public void ConvertsFour()
    {
        Assert.Equal("IV", RomanConverter.ToRoman(4));
    }

    [Fact]
    public void ConvertsForty()
    {
        Assert.Equal("XL", RomanConverter.ToRoman(40));
    }

    [Fact]
    public void ConvertsCompoundValue()
    {
        Assert.Equal("MCMXCIV", RomanConverter.ToRoman(1994));
    }
}
