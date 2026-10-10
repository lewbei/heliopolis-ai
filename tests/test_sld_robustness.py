"""Negative controls for the bounded SLD topology screen.

These are synthetic graph checks, not validation against real engineering drawings.
"""

import networkx as nx

from solar_agent import SLDTopologyResolver


def example_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    nodes = {
        "pv": "PV_Array",
        "inverter": "Inverter",
        "relay": "Anti_Islanding_Relay",
        "transformer": "Transformer",
        "grid": "Grid_Connection",
    }
    for name, category in nodes.items():
        graph.add_node(name, category=category)
    graph.add_edges_from([
        ("pv", "inverter"),
        ("inverter", "relay"),
        ("relay", "transformer"),
        ("transformer", "grid"),
    ])
    return graph


def test_normal_protected_graph_passes_preliminary_only():
    output = SLDTopologyResolver().validate_tnb_compliance(example_graph())
    assert output["grid_path_valid"] is True
    assert output["preliminary_topology_status"] == "PRELIMINARY_TOPOLOGY_PASS"
    assert "not a tnb" in output["scope_note"].lower()


def test_missing_inverter_fails_preliminary_graph():
    graph = example_graph()
    graph.remove_node("inverter")
    output = SLDTopologyResolver().validate_tnb_compliance(graph)
    assert not output["grid_path_valid"]
    assert "Missing modeled component: inverter" in output["findings"]


def test_reversed_transformer_connection_cannot_pass():
    graph = example_graph()
    graph.remove_edge("transformer", "grid")
    graph.add_edge("grid", "transformer")
    output = SLDTopologyResolver().validate_tnb_compliance(graph)
    assert not output["grid_path_valid"]
    assert output["disconnected_transformers"] == ["transformer"]


def test_multiple_transformers_requires_all_to_reach_grid():
    graph = example_graph()
    graph.add_node("transformer_2", category="Transformer")
    graph.add_edge("relay", "transformer_2")
    output = SLDTopologyResolver().validate_tnb_compliance(graph)
    assert not output["grid_path_valid"]
    assert "transformer_2" in output["disconnected_transformers"]


def test_relay_present_but_bypassed_is_flagged():
    graph = example_graph()
    graph.add_edge("inverter", "transformer")
    output = SLDTopologyResolver().validate_tnb_compliance(graph)
    assert not output["grid_path_valid"]
    assert any("bypass" in item.lower() for item in output["findings"])
