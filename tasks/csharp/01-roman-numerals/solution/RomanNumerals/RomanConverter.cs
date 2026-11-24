namespace RomanNumerals;

public static class RomanConverter
{
    private static readonly (int Value, string Symbol)[] _symbols =
    [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ];

    /// <summary>
    /// 1〜3999 の整数をローマ数字表記の文字列に変換する。
    /// </summary>
    public static string ToRoman(int value)
    {
        if (value is < 1 or > 3999)
        {
            throw new ArgumentOutOfRangeException(nameof(value), value, "value must be between 1 and 3999.");
        }

        var remaining = value;
        var builder = new System.Text.StringBuilder();
        foreach (var (symbolValue, symbol) in _symbols)
        {
            while (remaining >= symbolValue)
            {
                builder.Append(symbol);
                remaining -= symbolValue;
            }
        }

        return builder.ToString();
    }
}
