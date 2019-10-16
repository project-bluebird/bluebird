"""
Generates scenarios taking place within I, X, Y airspace sector elements.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import time
import numpy as np
import sys

import bluebird.scenario.sector_element as se

# JSON keys
CALLSIGN_KEY = "callsign"
TYPE_KEY = "type"
DEPARTURE_KEY = "departure"
DESTINATION_KEY = "destination"
START_POSITION_KEY = "startPosition"
START_TIME_KEY = "startTime"
CURRENT_FLIGHT_LEVEL_KEY = "currentFlightLevel"
CLEARED_FLIGHT_LEVEL_KEY = "clearedFlightLevel"
REQUESTED_FLIGHT_LEVEL_KEY = "requestedFlightLevel"
ROUTE_KEY = "route"
ROUTE_ELEMENT_NAME_KEY = "ROUTE_ELEMENT_NAME"
ROUTE_ELEMENT_TYPE_KEY = "ROUTE_ELEMENT_TYPE"
ROUTE_ELEMENT_SPEED_KEY = "ROUTE_ELEMENT_SPEED"
ROUTE_ELEMENT_LEVEL_KEY = "ROUTE_ELEMENT_LEVEL"
AIRCRAFT_KEY = "aircraft"

class ScenarioGenerator():
    """A scenario generator for I, X, Y airspace sectors"""

    # Default parameters:
    default_scenario_start_time = time.strptime("00:00:00", "%H:%M:%S") # Not to be confused with *aircraft* start time.
    default_aircraft_types = ["B747"] # Types of aircraft available (by default).
    default_flight_levels = [200, 240, 280, 320, 360, 400]

    # Fixed parameters:
    departure = "DEP"
    destination = "DEST"
    callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"]

    def __init__(self, sector_element, aircraft_types = None, flight_levels = None, start_time = None):

        self.sector_element = sector_element

        if aircraft_types is None:
            aircraft_types = ScenarioGenerator.default_aircraft_types
        self.aircraft_types = aircraft_types

        if flight_levels is None:
            flight_levels = ScenarioGenerator.default_flight_levels
        self.flight_levels = flight_levels

        if start_time is None:
            start_time = ScenarioGenerator.default_scenario_start_time
        self.start_time = start_time

    # TODO: add a route_indices argument to specify which routes to be included in the scenario.
    def poisson_scenario(self, arrival_rate, duration, seed = None):
        """Generates a random list of aircraft creation data whose arrivals in the sector form a Poisson process."""

        # Format the scenario start time.
        start_time = time.strftime("%H:%M:%S", self.start_time)

        interarrival_times = self.exponential_interarrival_times(arrival_rate = arrival_rate, duration = duration, seed = seed)

        n = len(interarrival_times)
        callsigns = self.callsigns(n = n, seed = seed)
        np.random.seed(seed=seed)
        aircraft_types = np.random.choice(self.aircraft_types, n, replace=True)

        # Randomly select from the available routes.
        np.random.seed(seed=seed)
        route_indices = np.random.choice(range(0, len(self.sector_element.shape.routes())), size = n, replace = True)  # With replacement.

        # Infer the aircraft start times from the interarrival times.
        # TODO: should these be added to the scenario start time?
        start_times = np.around(np.cumsum(interarrival_times)).astype(int)

        # Randomly select from the available flight levels to get the current level for each aircraft.
        np.random.seed(seed=seed)
        current_flight_levels = np.random.choice(self.flight_levels, size = n, replace = True)

        # Assume cleared flight level is always equal to current flight level.
        cleared_flight_levels = current_flight_levels
        np.random.seed(seed=seed)

        # Randomly select requested flight levels from the man/max available flight levels.
        requested_flight_levels = np.random.choice([min(self.flight_levels), max(self.flight_levels)], size = n, replace = True)

        ret = {
            START_TIME_KEY: start_time,
            AIRCRAFT_KEY: [self.aircraft(callsign = callsign,
                                         aircraft_type = aircraft_type,
                                         start_time = start_time,
                                         current_flight_level = current_flight_level,
                                         cleared_flight_level = cleared_flight_level,
                                         requested_flight_level = requested_flight_level,
                                         route_index = route_index
                                         )
                           for callsign, aircraft_type, start_time, current_flight_level,
                               cleared_flight_level, requested_flight_level, route_index
                           in zip(callsigns, aircraft_types, start_times, current_flight_levels,
                              cleared_flight_levels, requested_flight_levels, route_indices)]
        }
        return ret

    def aircraft(self, callsign, aircraft_type, start_time, current_flight_level,
                 cleared_flight_level, requested_flight_level, route_index) -> dict:
        """Returns all info required to create an aircraft, including its route."""

        # Infer the start position from the route (i.e. take the first fix).
        route = self.sector_element.shape.routes()[route_index]
        start_position = route[0][0]

        ret = {
            CALLSIGN_KEY: callsign,
            TYPE_KEY: aircraft_type,
            DEPARTURE_KEY: ScenarioGenerator.departure,
            DESTINATION_KEY: ScenarioGenerator.destination,
            START_POSITION_KEY: start_position,
            START_TIME_KEY: int(start_time),
            CURRENT_FLIGHT_LEVEL_KEY: int(current_flight_level),
            CLEARED_FLIGHT_LEVEL_KEY: int(cleared_flight_level),
            REQUESTED_FLIGHT_LEVEL_KEY: int(requested_flight_level),
            ROUTE_KEY: self.aircraft_route(route_index, speed = 0, level = requested_flight_level)
        }
        return ret

    def aircraft_route(self, route_index, speed = 0, level = 0) -> list:
        """Represents an aircraft's route as a list of (dictionary) route elements."""

        # Get the names of the fixes on the requested route.
        fix_names = [fix_items[0] for fix_items in self.sector_element.shape.routes()[route_index]]

        # Target speed and flight level are *always* applied to the last two route elements only.
        ret = [self.route_element(fix_name) for fix_name in fix_names[:len(fix_names) - 2]]
        ret.extend([self.route_element(fix_name, speed, level) for fix_name in fix_names[-2:]])
        return ret


    def route_element(self, fix_name, speed = 0, level = 0) -> dict:
        """Returns a dictionary representing a route element.
        Each route element has a name, a type (always 'FIX'), a target speed and a target flight level."""

        route_element = {
            ROUTE_ELEMENT_NAME_KEY: fix_name,
            ROUTE_ELEMENT_TYPE_KEY: se.FIX_VALUE,
            ROUTE_ELEMENT_SPEED_KEY: int(speed),
            ROUTE_ELEMENT_LEVEL_KEY: int(level)
        }
        return route_element

    def callsigns(self, n, seed = None):
        """Generates a list of up to 900 unique callsigns"""

        np.random.seed(seed=seed)
        suffixes = np.random.choice(range(0, 1000), size = n, replace = False) # without replacement.
        np.random.seed(seed=seed)
        prefixes = np.random.choice(ScenarioGenerator.callsign_prefixes, size = n, replace=True)

        return [pre + suf for pre, suf in zip(prefixes, [str(suffix) for suffix in suffixes])]

    def exponential_interarrival_times(self, arrival_rate, duration, seed = None):
        """Generates exponential interarrival times"""

        interarrival_times = []
        np.random.seed(seed = seed)
        while sum(interarrival_times) < duration:
            interarrival_times.append(np.random.exponential(scale = 1 / arrival_rate))

        # Guard against an empty list of interarrival times.
        if not interarrival_times:
            raise Exception('Empty interrarival times. Try increasing scenario duration and/or arrival rate.')

        return interarrival_times