"""
Tests for the MachColl sim client module
"""
from tests.unit.sim_client.common.imports_test import sim_client_instantiation
from tests.unit.sim_client.common.imports_test import sim_client_module_import

_MODULE_NAME = "MachColl"


def test_sim_client_module_import():
    """Test that the module can be imported without error"""
    failed = False
    try:
        sim_client_module_import(_MODULE_NAME)
    except ModuleNotFoundError:
        failed = True
    assert not failed


def test_sim_client_instantiation():
    """Tests that the SimClient can be instantiated"""
    failed = False
    try:
        sim_client_instantiation(_MODULE_NAME)
    except ModuleNotFoundError:
        failed = True
    assert not failed
