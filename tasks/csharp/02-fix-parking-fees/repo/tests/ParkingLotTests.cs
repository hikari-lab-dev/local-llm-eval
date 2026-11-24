namespace ParkingFees.Tests;

public class ParkingLotTests
{
    [Fact]
    public void ParkIncreasesOccupiedSpots()
    {
        var lot = new ParkingLot(totalSpots: 3);

        lot.Park();

        Assert.Equal(1, lot.OccupiedSpots);
    }

    [Fact]
    public void ReleaseDecreasesOccupiedSpots()
    {
        var lot = new ParkingLot(totalSpots: 3);
        lot.Park();

        lot.Release();

        Assert.Equal(0, lot.OccupiedSpots);
    }
}
