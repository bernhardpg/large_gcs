import numpy as np
from typing import List
from pydrake.all import (
    Variable,
    Polynomial,
    DecomposeAffineExpressions,
    DecomposeLinearExpressions,
    DecomposeQuadraticPolynomial,
    L2NormCost,
    LinearCost,
    QuadraticCost,
    LinearEqualityConstraint,
    LinearConstraint,
)
from large_gcs.contact.contact_set import ContactSetDecisionVariables


def create_vars_from_template(
    vars_template: np.ndarray, name_prefix: str
) -> np.ndarray:
    """Creates a new set of variables from a template"""
    vars_new = np.empty_like(vars_template)
    for i in range(vars_template.size):
        vars_new.flat[i] = Variable(
            f"{name_prefix}_{vars_template.flat[i].get_name()}",
            type=Variable.Type.CONTINUOUS,
        )
    return vars_new


### VERTEX COST CREATION ###


def vertex_cost_position_path_length(vars: ContactSetDecisionVariables) -> L2NormCost:
    """Creates a vertex cost that penalizes the length of the path in position space.
    vars.pos has shape (Euclidean/base dim, num positions/pos order per set)
    So to get the path length we need to diff over the second axis.
    """
    exprs = np.diff(vars.pos).flatten()
    A = DecomposeLinearExpressions(exprs, vars.all)
    b = np.zeros(A.shape[0])
    # print(f"vertex_cost_position_path_length A: {A}")
    return L2NormCost(A, b)


def vertex_cost_position_path_length_squared(
    vars: ContactSetDecisionVariables,
) -> QuadraticCost:
    path_length = np.diff(vars.pos).flatten()
    expr = np.dot(path_length, path_length)
    var_map = {var.get_id(): i for i, var in enumerate(vars.all)}
    Q, b, c = DecomposeQuadraticPolynomial(Polynomial(expr), var_map)
    return QuadraticCost(Q, b, c)


def vertex_cost_force_actuation_norm_squared(
    vars: ContactSetDecisionVariables,
) -> QuadraticCost:
    """Creates a vertex cost that penalizes the magnitude of the force actuation squared."""
    expr = np.dot(vars.force_act.flatten(), vars.force_act.flatten())
    var_map = {var.get_id(): i for i, var in enumerate(vars.all)}
    Q, b, c = DecomposeQuadraticPolynomial(Polynomial(expr), var_map)
    return QuadraticCost(Q, b, c)


### VERTEX CONSTRAINT CREATION ###


def vertex_constraint_force_act_limits(
    vars: ContactSetDecisionVariables, lb: np.ndarray, ub: np.ndarray
) -> LinearConstraint:
    """Creates a constraint that limits the magnitude of the force actuation in each dimension."""
    assert vars.force_act.size > 0
    raise NotImplementedError


### EDGE COST CREATION ###


def edge_cost_constant(
    u_vars: ContactSetDecisionVariables,
    v_vars: ContactSetDecisionVariables,
    constant_cost: float = 1,
) -> LinearCost:
    """Creates a cost that penalizes each active edge a constant value."""
    u_vars_all = create_vars_from_template(u_vars.all, "u")
    v_vars_all = create_vars_from_template(v_vars.all, "v")
    # Linear cost of the form: a'x + b, where a is a vector of coefficients and b is a constant.
    uv_vars_all = np.concatenate((u_vars_all, v_vars_all))
    a = np.zeros((uv_vars_all.size, 1))
    b = constant_cost
    return LinearCost(a, b)


def edge_costs_position_continuity_norm(
    u_vars: ContactSetDecisionVariables,
    v_vars: ContactSetDecisionVariables,
    linear_scaling: float = 1,
) -> L2NormCost:
    # Get the last position in u and first position in v
    u_vars_all = create_vars_from_template(u_vars.all, "u")
    v_vars_all = create_vars_from_template(v_vars.all, "v")
    u_pos = u_vars.pos_from_all(u_vars_all)
    v_pos = v_vars.pos_from_all(v_vars_all)
    u_last_pos = u_pos[:, :, -1].flatten()
    v_first_pos = v_pos[:, :, 0].flatten()
    uv_vars_all = np.concatenate((u_vars_all, v_vars_all))
    exprs = (u_last_pos - v_first_pos).flatten() * linear_scaling
    A = DecomposeLinearExpressions(exprs, uv_vars_all)
    b = np.zeros(A.shape[0])
    return L2NormCost(A, b)


### EDGE CONSTRAINT CREATION ###


def edge_constraint_position_continuity(
    u_vars: ContactSetDecisionVariables, v_vars: ContactSetDecisionVariables
) -> LinearEqualityConstraint:
    """Creates a constraint that enforces position continuity between the last position in vertex u to
    the first position in vertex v, given there's an edge from u to v. Since this is an edge constraint,
    the decision variables will be those of both the u and v vertices.
    """
    # Get the last position in u and first position in v
    u_vars_all = create_vars_from_template(u_vars.all, "u")
    v_vars_all = create_vars_from_template(v_vars.all, "v")
    u_pos = u_vars.pos_from_all(u_vars_all)
    v_pos = v_vars.pos_from_all(v_vars_all)
    u_last_pos = u_pos[:, :, -1].flatten()
    v_first_pos = v_pos[:, :, 0].flatten()
    uv_vars_all = np.concatenate((u_vars_all, v_vars_all))
    exprs = (u_last_pos - v_first_pos).flatten()
    # Linear equality constraint of the form: Ax = b
    A, b = DecomposeAffineExpressions(exprs, uv_vars_all)
    return LinearEqualityConstraint(A, b)
