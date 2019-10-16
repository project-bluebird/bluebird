
import pytest

import json

import bluebird.scenario.scenario_generator as sg
import bluebird.scenario.sector_shape as ss
import bluebird.scenario.sector_element as se

@pytest.fixture(scope="function")
def x_target():
    """Test fixture: a scenario generator operating on an X-shaped sector element."""

    name = "xshape"
    origin = (51.5, -0.1275)
    fix_names = ['sin', 'gates', 'siren', 'witch', 'abyss', 'haunt', 'limbo', 'demon', 'satan']
    shape = ss.XShape(fix_names = fix_names)
    lower_limit = 140
    upper_limit = 400
    x_sector = se.SectorElement(name, origin, shape, lower_limit, upper_limit)

    return sg.ScenarioGenerator(x_sector)

# Top to bottom route in X-sector is along fixes:
#   SIN (exterior top) -> GATES -> ABYSS (middle) -> HAUNT-> LIMBO (exterior bottom)
# Left to right route in X-sector is along fixes:
#   WITCH (exterior left) -> SIREN -> ABYSS (middle) -> DEMON -> SATAN (exterior right)

def test_route_element(x_target):

    fix_name = "SIN"
    level = 240
    result = x_target.route_element(fix_name = fix_name, level = level)

    assert sorted(result.keys()) == sorted([
        sg.ROUTE_ELEMENT_NAME_KEY,
        sg.ROUTE_ELEMENT_TYPE_KEY,
        sg.ROUTE_ELEMENT_SPEED_KEY,
        sg.ROUTE_ELEMENT_LEVEL_KEY])

    assert result[sg.ROUTE_ELEMENT_NAME_KEY] == fix_name
    assert result[sg.ROUTE_ELEMENT_TYPE_KEY] == se.FIX_VALUE
    assert result[sg.ROUTE_ELEMENT_SPEED_KEY] == 0
    assert result[sg.ROUTE_ELEMENT_LEVEL_KEY] == level

def test_aircraft_route(x_target):

    route_index = 0
    level = 240
    result = x_target.aircraft_route(route_index = route_index, level = level)
    assert isinstance(result, list)

    assert len(result) == len(x_target.sector_element.shape.routes()[route_index])

    # All ROUTE_ELEMENT_SPEED elements should be zero.
    for element_dict in result:
        assert element_dict[sg.ROUTE_ELEMENT_SPEED_KEY] == 0

    # All ROUTE_ELEMENT_LEVEL elements should be zero, except the last two, which should be 240.
    for element_dict in result[:len(result) - 2]:
        assert element_dict[sg.ROUTE_ELEMENT_LEVEL_KEY] == 0

    for element_dict in result[-2:]:
        assert element_dict[sg.ROUTE_ELEMENT_LEVEL_KEY] == level

    # import pprint
    # pprint.pprint(result)

def test_callsigns(x_target):

    n = 3
    result = x_target.callsigns(n)

    assert isinstance(result, list)
    assert len(result) == n
    assert all(isinstance(s, str) for s in result)


def test_aircraft(x_target):

    callsign = "SPEEDBIRD770"
    aircraft_type = "B747"

    route_index = 1

    start_time = 0
    current_flight_level = 260
    cleared_flight_level = 260
    requested_flight_level = 350

    result = x_target.aircraft(callsign = callsign, aircraft_type = aircraft_type, start_time = start_time,
                               current_flight_level = current_flight_level, cleared_flight_level = cleared_flight_level,
                               requested_flight_level = requested_flight_level, route_index = route_index)

    assert isinstance(result, dict)

    assert sg.CALLSIGN_KEY in result
    assert sg.ROUTE_KEY in result
    assert sg.START_TIME_KEY in result
    assert sg.START_POSITION_KEY in result

    assert len(result[sg.ROUTE_KEY]) == len(x_target.sector_element.shape.routes()[route_index])

    # Check that the start position matches the name of the first fix in the route.
    assert sg.ROUTE_ELEMENT_NAME_KEY in result[sg.ROUTE_KEY][0]
    assert result[sg.START_POSITION_KEY] == result[sg.ROUTE_KEY][0][sg.ROUTE_ELEMENT_NAME_KEY]

def test_exponential_interarrival_times(x_target):

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    duration = 5 * 60 # Five minute scenario
    seed = 74

    result = x_target.exponential_interarrival_times(arrival_rate = arrival_rate, duration = duration, seed = seed)

    # With this seed, there are 11 arrivals.
    assert len(result) == 11

def test_poisson_scenario(x_target):

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    duration = 5 * 60 # Five minute scenario
    seed = 74
    result = x_target.poisson_scenario(arrival_rate = arrival_rate, duration = duration, seed = seed)

    assert isinstance(result, dict)
    assert 'startTime' in result
    assert 'aircraft' in result

    assert isinstance(result['aircraft'], list)

    # With this seed, there are 11 arrivals.
    assert len(result['aircraft']) == 11

def test_serialisation(x_target):

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    duration = 1 * 60 # One minute scenario
    seed = 74
    result = x_target.poisson_scenario(arrival_rate = arrival_rate, duration = duration, seed = seed)

    serialised = json.dumps(result, sort_keys=True)

    deserialised = json.loads(serialised)

    assert isinstance(deserialised, dict)
    assert sorted(deserialised.keys()) == sorted([sg.AIRCRAFT_KEY, sg.START_TIME_KEY])

    #print(serialised)

