import time
import numpy as np
import scipy.interpolate as interpolate
import pressure

class Altimiter(object):
    """A reference altimiter is a time-series of pressure readings at a
    known altitude."""

    def __init__(self, altitude=0):
        """Create a new reference altimiter for the given altitude. The
        altimiter is initially empty (no pressure readings) and should
        be filled (by calling `ReferenceAltimiter.add_reading` at
        least once) before it is used.

        If no altitude is given the altimiter defaults to 0 meters
        above mean sea level (AMSL).

        """
        self._altitude = altitude
        self._pressure = []
        self._reference_interpolation = None

    def add_reading(self, reading, timestamp=None):
        """Add a pressure reading to the reference altimiter.

        If no timestamp is given the value of time.monotonic() is used.

        """
        if timestamp is None:
            self._pressure.append(pressure.TimeStampedPressure(reading, time.monotonic()))
        else:
            self._pressure.append(pressure.TimeStampedPressure(reading, timestamp))

        # discard any previously computed interpolation
        self._reference_interpolation = None
        self._pressure.sort(key=lambda tsp: tsp.timestamp)

    def adjust(self, readings):
        """Adjust readings according to the reference altimiter.

        If a reading is outside of the range of times for which there
        exists a valid reference pressure interpolation then it is
        discarded

        """
        times = np.array([ tsp.timestamp for tsp in self._pressure ])
        pressures = np.array([ tsp.pressure for tsp in self._pressure ])
        reference_interpolation = interpolate.interp1d(times, pressures)

        # perhaps more efficient if I converted the readings to a
        # numpy array and computed all adjustements at the same time,
        # but this will work for now
        min_time = self._pressure[0].timestamp
        max_time = self._pressure[-1].timestamp
        return [ self.adjust_pressure(reading) for reading in readings
                 if reading.timestamp > min_time and reading.timestamp < max_time ]

    def adjust_pressure(self, reading):
        """Adjust a single pressure according to the reference altimiter"""
        if self._reference_interpolation is None:
            times = np.array([tsp.timestamp for tsp in self._pressure ])
            pressures = np.array([ tsp.pressure for tsp in self._pressure ])
            self._reference_interpolation = interpolate.interp1d(times, pressures)

        cannonical_pressure = pressure.from_altitude(self._altitude)
        reference_pressure = reference_interpolation(reading.timestamp)
        pressure_difference = reading.pressure - reference_pressure
        return pressure_difference + cannonical_pressure
