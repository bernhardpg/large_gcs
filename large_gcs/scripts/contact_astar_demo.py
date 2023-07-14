from large_gcs.contact.contact_location import *
from large_gcs.contact.contact_pair_mode import *
from large_gcs.contact.rigid_body import *
from large_gcs.geometry.polyhedron import Polyhedron
from large_gcs.graph.contact_graph import ContactGraph
from large_gcs.algorithms.gcs_astar import GcsAstar
from large_gcs.algorithms.gcs_astar_subopt import GcsAstarSubOpt
from large_gcs.graph.contact_cost_constraint_factory import (
    contact_shortcut_edge_cost_factory,
)
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

np.set_printoptions(formatter={"float": lambda x: "{0:0.3f}".format(x)})
base = "contact_graph_triangle_challenge_full"
graph_file = os.path.join(
    os.environ["PROJECT_ROOT"], "large_gcs", "example_graphs", base + ".npy"
)
cg = ContactGraph.load_from_file(graph_file)
print(cg.params)

gcs_astar = GcsAstarSubOpt(
    cg,
    use_convex_relaxation=False,
    shortcut_edge_cost_factory=contact_shortcut_edge_cost_factory,
)
sol = gcs_astar.run(verbose=True, animate=False)

cg._post_solve(sol)
output_dir = os.path.join(os.environ["PROJECT_ROOT"], "output", "contact")
vid_file = os.path.join(output_dir, f"gcs_astar_{base}.mp4")

anim = cg.animate_solution()
anim.save(vid_file)
