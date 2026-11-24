namespace ParkingFees.HiddenTests;

public class ParkingLotHiddenTests
{
    [Fact]
    public void ParkThrowsWhenLotIsFull()
    {
        var lot = new ParkingLot(totalSpots: 1);
        lot.Park();

        Assert.Throws<InvalidOperationException>(lot.Park);
    }

    [Fact]
    public void ParkKeepsOccupiedCountWhenLotIsFull()
    {
        var lot = new ParkingLot(totalSpots: 1);
        lot.Park();
        var exception = Record.Exception(lot.Park);

        Assert.True(
            exception is InvalidOperationException && lot.OccupiedSpots == 1,
            $"exception={exception}, occupiedSpots={lot.OccupiedSpots}");
    }
}
