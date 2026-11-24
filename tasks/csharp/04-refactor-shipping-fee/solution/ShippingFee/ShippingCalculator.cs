namespace ShippingFee;

public static class ShippingCalculator
{
    private const decimal OverweightSurchargePerKilogram = 50m;
    private const decimal OverweightThresholdKilograms = 20m;
    private const decimal HeavyWeightThresholdKilograms = 50m;
    private const decimal HeavyWeightSurcharge = 1000m;
    private const decimal ExpressMultiplier = 1.5m;

    public static decimal CalculateFee(decimal weightKg, string region, bool express)
    {
        var baseFee = GetBaseFee(region);
        var total = ApplyWeightSurcharges(baseFee, weightKg);
        return express ? total * ExpressMultiplier : total;
    }

    private static decimal GetBaseFee(string region)
    {
        return region switch
        {
            "domestic" => 500m,
            "asia" => 1200m,
            "international" => 2500m,
            _ => throw new ArgumentException($"unknown region: {region}", nameof(region)),
        };
    }

    private static decimal ApplyWeightSurcharges(decimal baseFee, decimal weightKg)
    {
        var total = baseFee + GetOverweightSurcharge(weightKg);
        return weightKg > HeavyWeightThresholdKilograms
            ? total + HeavyWeightSurcharge
            : total;
    }

    private static decimal GetOverweightSurcharge(decimal weightKg)
    {
        return weightKg > OverweightThresholdKilograms
            ? (weightKg - OverweightThresholdKilograms) * OverweightSurchargePerKilogram
            : 0m;
    }
}
