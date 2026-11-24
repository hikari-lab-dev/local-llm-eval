namespace ShippingFee;

// リファクタリング対象。意図的にネストの深い1メソッド実装のまま置いている（課題: spec.md 参照）。
// else / 未分割メソッドはこの課題自体が指摘・修正させたい違反であり、意図的に残している。
public static class ShippingCalculator
{
    public static decimal CalculateFee(decimal weightKg, string region, bool express)
    {
        decimal baseFee;
        if (region == "domestic")
        {
            baseFee = 500m;
        }
        else
        {
            if (region == "asia")
            {
                baseFee = 1200m;
            }
            else
            {
                if (region == "international")
                {
                    baseFee = 2500m;
                }
                else
                {
                    throw new ArgumentException($"unknown region: {region}", nameof(region));
                }
            }
        }

        decimal total;
        if (weightKg > 20m)
        {
            total = baseFee + ((weightKg - 20m) * 50m);
        }
        else
        {
            total = baseFee;
        }

        if (weightKg > 50m)
        {
            total += 1000m;
        }

        if (express)
        {
            return total * 1.5m;
        }
        else
        {
            return total;
        }
    }
}
