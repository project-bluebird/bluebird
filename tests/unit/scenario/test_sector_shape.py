
import pytest

import sector_shape


def test_sector_type():

    i = sector_shape.IShape()
    assert i.sector_type == sector_shape.SectorType.I

    x = sector_shape.XShape()
    assert x.sector_type == sector_shape.SectorType.X

    y = sector_shape.YShape()
    assert y.sector_type == sector_shape.SectorType.Y

    # Test immutability of the sector_type
    with pytest.raises(Exception):
        i.sector_type = sector_shape.SectorType.X

    assert i.sector_type == sector_shape.SectorType.I


def test_i_fixes():

    fix_names = ['a', 'b', 'c', 'd', 'e']
    i = sector_shape.IShape(fix_names=fix_names)
    assert list(i.fixes.keys()) == [fix_name.upper() for fix_name in fix_names]

    with pytest.raises(ValueError):
        sector_shape.IShape(fix_names = ['a', 'b', 'c'])


def test_x_fixes():

    fix_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    x = sector_shape.XShape(fix_names=fix_names)
    assert list(x.fixes.keys()) == [fix_name.upper() for fix_name in fix_names]


def test_y_fixes():

    fix_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    y = sector_shape.YShape(fix_names=fix_names)
    assert list(y.fixes.keys()) == [fix_name.upper() for fix_name in fix_names]

def test_i_routes():

    length_nm = 10
    i = sector_shape.IShape(length_nm=length_nm)
    result = i.routes()

    # There are two routes: ascending/descending along the y-axis.
    assert len(result) == 2

    # Each route contains five fixes.
    assert len(result[0]) == 5
    assert len(result[1]) == 5

    # Each element of 'result' is a list of dictionary items (representing fixes) of the form: (name, Point).

    # result[0] is ascending along the y-axis
    assert result[0][0][1].coords[0][1] == -1 * (i.offset_nm + (length_nm / 2))
    assert result[0][1][1].coords[0][1] == -1 * (length_nm / 2)
    assert result[0][2][1].coords[0][1] == 0
    assert result[0][3][1].coords[0][1] == length_nm / 2
    assert result[0][4][1].coords[0][1] == i.offset_nm + (length_nm / 2)

    # result[1] is descending along the y-axis
    assert result[1][0][1].coords[0][1] == i.offset_nm + (length_nm / 2)
    assert result[1][1][1].coords[0][1] == length_nm / 2
    assert result[1][2][1].coords[0][1] == 0
    assert result[1][3][1].coords[0][1] == -1 * (length_nm / 2)
    assert result[1][4][1].coords[0][1] == -1 * (i.offset_nm + (length_nm / 2))


def test_x_routes():

    length_nm = 10
    x = sector_shape.XShape(length_nm=length_nm)
    result = x.routes()

    # There are four routes: ascending/descending in the y-coordinate and ascending/descending in the x-coordinate.
    assert len(result) == 4

    # Each route contains five fixes.
    assert len(result[0]) == 5
    assert len(result[1]) == 5
    assert len(result[2]) == 5
    assert len(result[3]) == 5

    # Each element of 'result' is a list of dictionary items (representing fixes) of the form: (name, Point).

    # result[0] is ascending along the y-axis
    assert result[0][0][1].coords[0][1] == -1 * (x.offset_nm + (length_nm / 2))
    assert result[0][1][1].coords[0][1] == -1 * (length_nm / 2)
    assert result[0][2][1].coords[0][1] == 0
    assert result[0][3][1].coords[0][1] == length_nm / 2
    assert result[0][4][1].coords[0][1] == x.offset_nm + (length_nm / 2)

    # result[1] is descending along the y-axis
    assert result[1][0][1].coords[0][1] == x.offset_nm + (length_nm / 2)
    assert result[1][1][1].coords[0][1] == length_nm / 2
    assert result[1][2][1].coords[0][1] == 0
    assert result[1][3][1].coords[0][1] == -1 * (length_nm / 2)
    assert result[1][4][1].coords[0][1] == -1 * (x.offset_nm + (length_nm / 2))


# TODO.
def test_y_routes():
    pass

def test_i_named_routes():

    i = sector_shape.IShape()

    result = i.named_routes()
    assert isinstance(result, dict)

    assert sorted(result.keys()) == sorted(i.route_names)

    assert isinstance(result[i.route_names[0]], list)
    assert len(result[i.route_names[0]]) == len(i.routes()[0])
    assert len(result[i.route_names[1]]) == len(i.routes()[1])
