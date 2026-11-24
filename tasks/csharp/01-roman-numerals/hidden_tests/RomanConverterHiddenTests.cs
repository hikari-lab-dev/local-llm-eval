using RomanNumerals;

namespace RomanNumerals.HiddenTests;

public class RomanConverterHiddenTests
{
    [Fact]
    public void ConvertsNine()
    {
        Assert.Equal("IX", RomanConverter.ToRoman(9));
    }

    [Fact]
    public void ConvertsNinety()
    {
        Assert.Equal("XC", RomanConverter.ToRoman(90));
    }

    [Fact]
    public void ConvertsNineHundred()
    {
        Assert.Equal("CM", RomanConverter.ToRoman(900));
    }

    [Fact]
    public void ConvertsMixedSubtractiveValue()
    {
        Assert.Equal("LVIII", RomanConverter.ToRoman(58));
    }

    [Fact]
    public void ConvertsMaxValue()
    {
        Assert.Equal("MMMCMXCIX", RomanConverter.ToRoman(3999));
    }

    [Fact]
    public void ConvertsMinValue()
    {
        Assert.Equal("I", RomanConverter.ToRoman(1));
    }

    [Fact]
    public void ThrowsWhenValueIsBelowRange()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => RomanConverter.ToRoman(0));
    }

    [Fact]
    public void ThrowsWhenValueIsAboveRange()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => RomanConverter.ToRoman(4000));
    }
}
