import numpy as np
from dataclasses import dataclass
import itertools
import matplotlib.pyplot as plt
from typing import List
from pydrake.all import (
    Variables,
    DecomposeAffineExpressions,
    HPolyhedron,
    Point as DrakePoint,
    Formula,
    FormulaKind,
    le,
)

from large_gcs.contact.contact_pair_mode import (
    ContactPairMode,
    InContactPairMode,
)
from large_gcs.contact.rigid_body import RigidBody, MobilityType
from large_gcs.geometry.convex_set import ConvexSet


@dataclass
class ContactSetDecisionVariables:
    pos: np.ndarray
    force_res: np.ndarray
    force_act: np.ndarray
    force_mag_AB: np.ndarray
    force_mag_BA: np.ndarray
    all: np.ndarray
    base_all: np.ndarray

    @classmethod
    def from_contact_pair_modes(
        cls,
        objects: List[RigidBody],
        robots: List[RigidBody],
        contact_pair_modes: List[ContactPairMode],
    ):
        pos = np.array([body.vars_pos for body in objects + robots])
        force_res = np.array([body.vars_force_res for body in objects + robots])

        force_act = np.array([body.vars_force_act for body in robots])
        in_contact_pair_modes = [
            mode for mode in contact_pair_modes if isinstance(mode, InContactPairMode)
        ]
        force_mag_AB = np.array(
            [mode.vars_force_mag_AB for mode in in_contact_pair_modes]
        )
        force_mag_BA = np.array(
            [mode.vars_force_mag_BA for mode in in_contact_pair_modes]
        )

        # All the decision variables for a single vertex
        all = np.concatenate(
            (
                pos.flatten(),
                force_res.flatten(),
                force_act.flatten(),
                force_mag_AB.flatten(),
                force_mag_BA.flatten(),
            )
        )
        # Extract the first point in n_pos_points_per_set
        base_all = np.array(
            [body.vars_pos[:, 0] for body in objects + robots]
        ).flatten()

        return cls(pos, force_res, force_act, force_mag_AB, force_mag_BA, all, base_all)

    def pos_from_all(self, vars_all):
        """Extracts the vars_pos from vars_all and reshapes it to match the template"""
        return np.reshape(vars_all[: self.pos.size], self.pos.shape)

    def force_res_from_vars(self, vars_all):
        return np.reshape(
            vars_all[self.pos.size : self.pos.size + self.force_res.size],
            self.force_res.shape,
        )

    @classmethod
    def from_pos_singleton(cls, objects, robots):
        pos = np.array([body.vars_pos[:, 0] for body in objects + robots])
        pos = pos[:, :, np.newaxis]
        empty = np.array([])
        return cls(pos, empty, empty, empty, empty, pos.flatten(), pos.flatten())


class ContactPointSet(ConvexSet):
    def __init__(
        self,
        id: str,
        objects: List[RigidBody],
        robots: List[RigidBody],
        object_positions: List[np.ndarray],
        robot_positions: List[np.ndarray],
    ):
        assert len(objects) == len(object_positions)
        assert len(robots) == len(robot_positions)
        # Check that all object and robot positions have the same dimension
        positions = np.array(object_positions + robot_positions)
        assert len(set([pos.shape[0] for pos in positions])) == 1
        assert positions.shape[1] == robots[0].dim

        self.vars = ContactSetDecisionVariables.from_pos_singleton(objects, robots)
        self._point = DrakePoint(positions.flatten())

        self._id = id

    @property
    def id(self):
        return self._id

    @property
    def dim(self):
        return self.set.ambient_dimension()

    @property
    def set(self):
        return self._point

    @property
    def base_set(self):
        return self._point

    @property
    def center(self):
        return None


class ContactSet(ConvexSet):
    def __init__(
        self,
        contact_pair_modes: List[ContactPairMode],
        additional_constraints: List[Formula],
        objects: List[RigidBody],
        robots: List[RigidBody],
    ):
        if not all(obj.mobility_type == MobilityType.UNACTUATED for obj in objects):
            raise ValueError("All objects must be unactuated")
        if not all(robot.mobility_type == MobilityType.ACTUATED for robot in robots):
            raise ValueError("All robots must be actuated")

        self.vars = ContactSetDecisionVariables.from_contact_pair_modes(
            objects, robots, contact_pair_modes
        )
        # print(f"set_force_constraints shape: {np.array(set_force_constraints).shape}")
        # print(f"set_force_constraints: {set_force_constraints}")

        self.contact_pair_modes = contact_pair_modes
        self.constraint_formulas = [
            constraint.item()
            for mode in contact_pair_modes
            for constraint in mode.constraint_formulas
        ]
        self.base_constraint_formulas = [
            constraint.item()
            for mode in contact_pair_modes
            for constraint in mode.base_constraint_formulas
        ]
        self.constraint_formulas.extend(additional_constraints)
        self._polyhedron = self._construct_polyhedron_from_constraints(
            self.constraint_formulas, self.vars.all
        )
        self._base_polyhedron = self._construct_polyhedron_from_constraints(
            self.base_constraint_formulas, self.vars.base_all
        )
        # print(f"set id: {self.id}")
        # print(f"all vars {all_variables}")
        # print(f"base all vars {base_all_variables}")
        # print()

    def _construct_polyhedron_from_constraints(
        self,
        constraints: List[Formula],
        variables: np.ndarray,
        make_bounded: bool = True,
        BOUND: float = 1000.0,
    ):
        """
        Construct a polyhedron from a list of constraint formulas.
        Args:
            constraints: array of constraint formulas.
            variables: array of variables.
        """
        if make_bounded:
            ub = np.ones(variables.shape) * BOUND
            upper_limits = le(variables, ub)
            lower_limits = le(-ub, variables)
            limits = np.concatenate((upper_limits, lower_limits))
            constraints = np.append(constraints, limits)

        expressions = []
        # print(f"Constructing polyhedron for set {self.id}")
        # print(f"variables: {variables}")
        for formula in constraints:
            # print(formula)
            kind = formula.get_kind()
            lhs, rhs = formula.Unapply()[1]
            if kind == FormulaKind.Eq:
                # Eq constraint ax = b is
                # implemented as ax ≤ b, -ax <= -b
                expressions.append(lhs - rhs)
                expressions.append(rhs - lhs)
            elif kind == FormulaKind.Geq:
                # lhs >= rhs
                # ==> rhs - lhs ≤ 0
                expressions.append(rhs - lhs)
            elif kind == FormulaKind.Leq:
                # lhs ≤ rhs
                # ==> lhs - rhs ≤ 0
                expressions.append(lhs - rhs)
            else:
                raise NotImplementedError("Type of constraint formula not implemented")

        # We now have expr ≤ 0 for all expressions
        # ==> we get Ax - b ≤ 0
        A, b_neg = DecomposeAffineExpressions(expressions, variables)

        # Polyhedrons are of the form: Ax <= b
        b = -b_neg
        polyhedron = HPolyhedron(A, b)

        return polyhedron

    @property
    def id(self):
        return tuple([mode.id for mode in self.contact_pair_modes])

    @property
    def dim(self):
        return self.set.A().shape[1]

    @property
    def set(self):
        return self._polyhedron

    @property
    def base_set(self):
        return self._base_polyhedron

    @property
    def center(self):
        return None
