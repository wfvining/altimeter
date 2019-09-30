class TimeStampedPressure(object):
    """Pressure reading with a time. We can define an ordering over these
    based on their time stamp.

    """

    def __init__(self, pressure, timestamp):
        self.timestamp = timestamp
        self.pressure  = pressure

def to_altitude(pressure_mbar):
    """Calculate altitude in meters from pressure in millibars."""
    # this formula is from weather.gov, so naturally it mixes units
    # (pressure in mbar altitude in ft) we multiply by 0.3048 to get
    # meters
    return ((1.0 - (pressure_mbar / 1013.25)**0.190284) * 145366.45) / 3.2804

def from_altitude(altitude_meters):
    """Calculate "cannonical" pressure in millibars from altitude in meters"""
    altitude_feet = altitude_meters * 3.2804
    return 1013.25*(1.0 - altitude_feet / 145366.45)**(1.0 / 0.190284)
