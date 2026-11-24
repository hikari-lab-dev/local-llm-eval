namespace ParkingFees;

public sealed class ParkingLot
{
    private int _occupiedSpots;

    public ParkingLot(int totalSpots)
    {
        TotalSpots = totalSpots;
    }

    public int TotalSpots { get; }

    public int OccupiedSpots => _occupiedSpots;

    public void Park()
    {
        if (_occupiedSpots >= TotalSpots)
        {
            throw new InvalidOperationException("満車です。");
        }

        _occupiedSpots++;
    }

    public void Release()
    {
        if (_occupiedSpots > 0)
        {
            _occupiedSpots--;
        }
    }
}
