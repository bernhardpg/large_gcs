import numpy as np
import pytest

from large_gcs.algorithms.gcs_astar_convex_restriction import GcsAstarConvexRestriction
from large_gcs.algorithms.search_algorithm import ReexploreLevel
from large_gcs.cost_estimators.factored_collision_free_ce import FactoredCollisionFreeCE
from large_gcs.graph.contact_cost_constraint_factory import (
    contact_shortcut_edge_cost_factory_over_obj_weighted,
)
from large_gcs.graph.contact_graph import ContactGraph
from large_gcs.graph.graph import ShortestPathSolution
from large_gcs.graph.incremental_contact_graph import IncrementalContactGraph
from large_gcs.graph_generators.contact_graph_generator import (
    ContactGraphGeneratorParams,
)

tol = 1e-3


def test_convert_to_cfree_vertex_names_mult_objs():
    vertex_name = "('NC|obs0_f3-obj0_v1', 'NC|obs0_f3-obj1_v1', 'NC|obs0_f3-rob0_v1', 'NC|obj0_f1-obj1_f3', 'NC|obj0_f2-rob0_f0', 'NC|obj1_f2-rob0_f0')"
    cfree_vertex_names = [
        "('NC|obs0_f3-obj0_v1',)",
        "('NC|obs0_f3-obj1_v1',)",
        "('NC|obs0_f3-rob0_v1',)",
    ]
    assert (
        FactoredCollisionFreeCE.convert_to_cfree_vertex_names(vertex_name)
        == cfree_vertex_names
    )


@pytest.mark.slow_test
def test_cfree_conv_res_cg_simple_2():
    graph_file = ContactGraphGeneratorParams.graph_file_path_from_name("cg_simple_2")
    cg = ContactGraph.load_from_file(graph_file)
    cost_estimator = FactoredCollisionFreeCE(
        cg,
        use_combined_gcs=False,
        add_transition_cost=True,
        obj_multiplier=2.0,
    )
    gcs_astar = GcsAstarConvexRestriction(
        cg,
        cost_estimator=cost_estimator,
        reexplore_level=ReexploreLevel.FULL,
    )
    sol: ShortestPathSolution = gcs_astar.run()
    ambient_path = [
        [0.000, 0.000, -2.000, -2.000],
        [
            0.000,
            -0.000,
            0.000,
            0.000,
            -2.000,
            -0.733,
            -2.000,
            -0.500,
            -0.000,
            -0.000,
            1.267,
            1.500,
            1.267,
            1.500,
        ],
        [
            -0.000,
            2.000,
            0.000,
            0.000,
            -0.733,
            1.267,
            -0.500,
            0.500,
            2.000,
            -0.000,
            2.000,
            1.000,
            2.000,
            1.000,
            0.000,
            2.000,
        ],
        [
            2.000,
            2.000,
            0.000,
            0.000,
            1.267,
            1.467,
            0.500,
            1.000,
            -0.000,
            -0.000,
            0.200,
            0.500,
            0.200,
            0.500,
            0.000,
            -0.000,
        ],
        [
            2.000,
            2.000,
            -0.000,
            0.000,
            1.467,
            2.500,
            1.000,
            2.000,
            -0.000,
            -0.000,
            1.033,
            1.000,
            1.033,
            1.000,
        ],
        [2.000, 0.000, 2.500, 2.000],
    ]
    vertex_path = np.array(
        [
            "source",
            "('NC|obj0_f3-rob0_v0',)",
            "('IC|obj0_f3-rob0_v0',)",
            "('IC|obj0_v3-rob0_f2',)",
            "('NC|obj0_f2-rob0_v2',)",
            "target",
        ]
    )
    assert np.isclose(sol.cost, 11.939768211912497, atol=tol)
    assert all(
        np.allclose(v, v_sol, atol=tol)
        for v, v_sol in zip(sol.ambient_path, ambient_path)
    )
    assert np.array_equal(sol.vertex_path, vertex_path)


@pytest.mark.slow_test
def test_cfree_conv_res_cg_trichal2():
    graph_file = ContactGraphGeneratorParams.graph_file_path_from_name("cg_trichal2")
    cg = ContactGraph.load_from_file(graph_file)
    cost_estimator = FactoredCollisionFreeCE(
        cg,
        use_combined_gcs=False,
        add_transition_cost=True,
        obj_multiplier=2.0,
    )
    gcs_astar = GcsAstarConvexRestriction(
        cg,
        cost_estimator=cost_estimator,
        reexplore_level=ReexploreLevel.NONE,
    )
    sol: ShortestPathSolution = gcs_astar.run()
    ambient_path = [
        [3.250, 0.000, 1.500, 0.500],
        [
            3.250,
            3.250,
            0.000,
            0.000,
            1.500,
            2.417,
            0.500,
            0.833,
            -0.000,
            -0.000,
            0.917,
            0.333,
            0.917,
            0.333,
        ],
        [
            3.250,
            3.250,
            0.000,
            -2.500,
            2.417,
            3.917,
            0.833,
            -1.667,
            -0.000,
            -2.500,
            1.500,
            -2.500,
            1.500,
            -2.500,
            0.000,
            2.500,
        ],
        [
            3.250,
            -1.500,
            -2.500,
            -2.500,
            3.917,
            -0.833,
            -1.667,
            -3.667,
            -4.750,
            -0.000,
            -4.750,
            -2.000,
            -4.750,
            -2.000,
            0.000,
            4.750,
        ],
        [
            -1.500,
            -1.500,
            -2.500,
            -1.500,
            -0.833,
            -1.833,
            -3.667,
            -2.667,
            -0.000,
            1.000,
            -1.000,
            1.000,
            -1.000,
            1.000,
            0.000,
            1.000,
        ],
        [
            -1.500,
            -1.500,
            -1.500,
            0.000,
            -1.833,
            -2.333,
            -2.667,
            -0.167,
            -0.000,
            1.500,
            -0.500,
            2.500,
            -0.500,
            2.500,
            3.000,
            0.000,
            3.000,
            3.354,
        ],
        [
            -1.500,
            -1.500,
            0.000,
            0.000,
            -2.333,
            -3.000,
            -0.167,
            0.000,
            -0.000,
            -0.000,
            -0.667,
            0.167,
            -0.667,
            0.167,
            0.000,
            0.000,
        ],
        [-1.500, 0.000, -3.000, 0.000],
    ]
    vertex_path = np.array(
        [
            "source",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'NC|obj0_f3-rob0_v0')",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f2-rob0_f2')",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f1-rob0_f1')",
            "('NC|obs0_f2-obj0_f1', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f0-rob0_v1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_f2-rob0_v0', 'IC|obj0_v0-rob0_f0')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_f2-rob0_v0', 'NC|obj0_f3-rob0_v0')",
            "target",
        ]
    )
    assert np.isclose(sol.cost, 24.20215518801082, atol=tol)
    assert all(
        np.allclose(v, v_sol, atol=tol)
        for v, v_sol in zip(sol.ambient_path, ambient_path)
    )
    assert np.array_equal(sol.vertex_path, vertex_path)


@pytest.mark.slow_test
def test_cfree_conv_res_cg_trichal2_inc_wo_combined_gcs():
    graph_file = ContactGraphGeneratorParams.inc_graph_file_path_from_name(
        "cg_trichal2"
    )
    cg = IncrementalContactGraph.load_from_file(
        graph_file,
        should_incl_simul_mode_switches=False,
        should_add_const_edge_cost=False,
        should_add_gcs=False,
    )
    cost_estimator = FactoredCollisionFreeCE(
        cg,
        use_combined_gcs=False,
        add_transition_cost=True,
        obj_multiplier=100.0,
    )
    gcs_astar = GcsAstarConvexRestriction(
        cg,
        cost_estimator=cost_estimator,
        reexplore_level=ReexploreLevel.NONE,
    )
    sol: ShortestPathSolution = gcs_astar.run()
    # fmt: off
    ambient_path = [
       [3.250, 0.000, 1.500, 0.500], [ 3.250, 3.250, 0.000, 0.000, 1.500, 2.417, 0.500, 0.833, -0.000, -0.000, 0.917, 0.333, 0.917, 0.333, ], [ 3.250, 3.250, 0.000, -1.500, 2.417, 3.917, 0.833, -0.667, -0.000, -1.500, 1.500, -1.500, 1.500, -1.500, 0.000, 1.500, ], [ 3.250, 3.250, -1.500, -1.500, 3.917, 3.917, -0.667, -0.667, -0.000, -0.000, 0.000, -0.000, 0.000, -0.000, 0.000, -0.000, ], [ 3.250, -1.500, -1.500, -1.500, 3.917, -0.833, -0.667, -2.667, -4.750, -0.000, -4.750, -2.000, -4.750, -2.000, 0.000, 4.750, ], [ -1.500, -1.500, -1.500, -1.500, -0.833, -0.833, -2.667, -2.667, -0.000, -0.000, -0.000, -0.000, -0.000, -0.000, -0.000, 0.000, -0.000, -0.000, ], [ -1.500, -1.500, -1.500, -1.500, -0.833, -0.833, -2.667, -2.667, -0.000, -0.000, -0.000, -0.000, -0.000, -0.000, -0.000, 0.000, -0.000, -0.000, ], [ -1.500, -1.500, -1.500, -1.500, -0.833, -0.833, -2.667, -2.667, -0.000, -0.000, -0.000, -0.000, -0.000, -0.000, 0.000, -0.000, ], [ -1.500, -1.500, -1.500, -1.500, -0.833, -0.833, -2.667, -2.667, -0.000, -0.000, 0.000, -0.000, 0.000, -0.000, ], [ -1.500, -1.500, -1.500, -1.500, -0.833, -0.833, -2.667, -2.667, -0.000, -0.000, -0.000, -0.000, -0.000, -0.000, 0.000, 0.000, ], [ -1.500, -1.500, -1.500, -0.556, -0.833, -1.463, -2.667, -1.723, -0.000, 0.944, -0.629, 0.944, -0.629, 394.032, 0.000, 393.088, 0.000, 0.944, ], [ -1.500, -1.500, -0.556, -0.272, -1.463, -1.652, -1.723, -1.438, -0.000, 0.285, -0.190, 0.285, -0.190, 410.953, 0.000, 410.668, 0.000, 0.285, ], [ -1.500, -1.500, -0.272, -0.000, -1.652, -1.833, -1.438, -1.167, -0.000, 0.272, -0.181, 0.272, -0.181, 395.305, 395.034, 0.272, ], [ -1.500, -1.500, -0.000, 0.000, -1.833, -3.000, -1.167, 0.000, -0.000, -0.000, -1.167, 1.167, -1.167, 1.167, ], [-1.500, 0.000, -3.000, 0.000], 
    ]
    # fmt: on
    vertex_path = np.array(
        [
            "source",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'NC|obj0_f3-rob0_v0')",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f2-rob0_f2')",
            "('NC|obs0_v0-obj0_f2', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f2-rob0_f2')",
            "('NC|obs0_v0-obj0_f2', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f1-rob0_f1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f1-rob0_f1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'IC|obj0_f1-rob0_f1')",
            "('NC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'IC|obj0_f1-rob0_f1')",
            "('NC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'NC|obj0_f1-rob0_f1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'NC|obj0_f1-rob0_f1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'IC|obj0_f0-rob0_v1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_f2-rob0_v0', 'IC|obj0_f0-rob0_v1')",
            "('NC|obs0_f2-obj0_f1', 'NC|obs0_f2-rob0_v0', 'IC|obj0_f0-rob0_v1')",
            "('NC|obs0_f2-obj0_f1', 'NC|obs0_f2-rob0_v0', 'NC|obj0_v0-rob0_f0')",
            "target",
        ]
    )
    assert np.isclose(sol.cost, 14.577507245424258, atol=tol)
    for v, v_sol in zip(sol.ambient_path, ambient_path):
        assert np.allclose(v, v_sol, atol=tol)
    assert np.array_equal(sol.vertex_path, vertex_path)


@pytest.mark.slow_test
def test_cfree_conv_res_cg_trichal2_inc_use_combined_gcs():
    graph_file = ContactGraphGeneratorParams.inc_graph_file_path_from_name(
        "cg_trichal2"
    )
    cg = IncrementalContactGraph.load_from_file(
        graph_file,
        should_incl_simul_mode_switches=False,
        should_add_const_edge_cost=True,
        should_add_gcs=True,
    )
    cost_estimator = FactoredCollisionFreeCE(
        cg,
        use_combined_gcs=True,
        add_transition_cost=True,
        obj_multiplier=100.0,
    )
    gcs_astar = GcsAstarConvexRestriction(
        cg,
        cost_estimator=cost_estimator,
        reexplore_level=ReexploreLevel.NONE,
    )
    sol: ShortestPathSolution = gcs_astar.run()
    ambient_path = [
        [3.250, 0.000, 1.500, 0.500],
        [
            3.250,
            3.250,
            0.000,
            0.000,
            1.500,
            2.417,
            0.500,
            0.833,
            -0.000,
            -0.000,
            0.917,
            0.333,
            0.917,
            0.333,
        ],
        [
            3.250,
            3.250,
            0.000,
            -1.500,
            2.417,
            3.917,
            0.833,
            -0.667,
            -0.000,
            -1.500,
            1.500,
            -1.500,
            1.500,
            -1.500,
            0.000,
            1.500,
        ],
        [
            3.250,
            -0.500,
            -1.500,
            -1.500,
            3.917,
            0.167,
            -0.667,
            -2.246,
            -3.750,
            -0.000,
            -3.750,
            -1.579,
            -3.750,
            -1.579,
            0.000,
            3.750,
        ],
        [
            -0.500,
            -1.153,
            -1.500,
            -1.500,
            0.167,
            -0.486,
            -2.246,
            -2.521,
            -0.653,
            -0.000,
            -0.653,
            -0.275,
            -400.484,
            -0.275,
            0.000,
            399.830,
            0.000,
            0.653,
        ],
        [
            -1.153,
            -1.500,
            -1.500,
            -1.500,
            -0.486,
            -0.833,
            -2.521,
            -2.667,
            -0.347,
            -0.000,
            -0.347,
            -0.146,
            -397.283,
            -0.146,
            0.000,
            396.936,
            0.000,
            0.347,
        ],
        [
            -1.500,
            -1.500,
            -1.500,
            -1.500,
            -0.833,
            -0.833,
            -2.667,
            -2.667,
            -0.000,
            -0.000,
            -0.000,
            -0.000,
            -0.000,
            -0.000,
            -0.000,
            0.000,
            -0.000,
            -0.000,
        ],
        [
            -1.500,
            -1.500,
            -1.500,
            0.000,
            -0.833,
            -1.833,
            -2.667,
            -1.167,
            -0.000,
            1.500,
            -1.000,
            1.500,
            -1.000,
            1.500,
            0.000,
            0.000,
            0.000,
            1.500,
        ],
        [
            -1.500,
            -1.500,
            0.000,
            0.000,
            -1.833,
            -3.000,
            -1.167,
            0.000,
            -0.000,
            -0.000,
            -1.167,
            1.167,
            -1.167,
            1.167,
            0.000,
            0.000,
        ],
        [-1.500, 0.000, -3.000, 0.000],
    ]
    vertex_path = np.array(
        [
            "source",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'NC|obj0_f3-rob0_v0')",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f2-rob0_f2')",
            "('NC|obs0_f0-obj0_v3', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f1-rob0_f1')",
            "('IC|obs0_v0-obj0_f2', 'NC|obs0_f0-rob0_v1', 'IC|obj0_f1-rob0_f1')",
            "('IC|obs0_v0-obj0_f2', 'NC|obs0_v0-rob0_f0', 'IC|obj0_f1-rob0_f1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'IC|obj0_f1-rob0_f1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'IC|obj0_f0-rob0_v1')",
            "('IC|obs0_f2-obj0_f1', 'NC|obs0_v0-rob0_f0', 'NC|obj0_v0-rob0_f0')",
            "target",
        ]
    )
    assert np.isclose(sol.cost, 23.577507032828205, atol=tol)
    assert all(
        np.allclose(v, v_sol, atol=tol)
        for v, v_sol in zip(sol.ambient_path, ambient_path)
    )
    assert np.array_equal(sol.vertex_path, vertex_path)
