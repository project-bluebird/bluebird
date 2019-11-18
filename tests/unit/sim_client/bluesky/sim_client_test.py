"""
Tests that the BlueSky sim client module can be imported without error
"""

from tests.unit.sim_client.common.imports import (
    sim_client_module_import,
    abstract_class_implementation,
)

_MODULE_NAME = "BlueSky"


def test_sim_client_module_import():
    """Test that the module can be imported without error"""
    sim_client_module_import(_MODULE_NAME)


def test_abstract_class_implementation():
    """Tests that the abstract classes are properly implemented"""
    abstract_class_implementation(_MODULE_NAME)
