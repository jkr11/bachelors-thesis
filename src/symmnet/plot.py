from symmnet.symmetry import Fib, SU2
from symmnet.fusiontree import FusionTree, OpenEdge, InternalEdge, NodeType
import numpy as np


def plot_ascii_fusion_tree(nodes, spacing=6):
  parent_map = {c: (a, b) for a, b, c in nodes}
  children = {a for a, b, c in nodes} | {b for a, b, c in nodes}
  parents = {c for a, b, c in nodes}
  roots = list(parents - children)

  if not roots:
    raise ValueError("Invalid fusion tree structure: no root found.")

  def build_tree(item):
    if item in parent_map:
      left, right = parent_map[item]
      return (build_tree(left), build_tree(right))
    return item

  tree = build_tree(roots[0])

  leaves = []

  def collect_leaves(t):
    if isinstance(t, tuple):
      collect_leaves(t[0])
      collect_leaves(t[1])
    else:
      leaves.append(t)

  collect_leaves(tree)

  def compute_positions(t, leaf_offset):
    if not isinstance(t, tuple):
      return {"x": leaf_offset * spacing, "y": 0, "type": "leaf", "label": str(t), "count": 1}

    left_info = compute_positions(t[0], leaf_offset)
    right_info = compute_positions(t[1], leaf_offset + left_info["count"])

    x_L, y_L = left_info["x"], left_info["y"]
    x_R, y_R = right_info["x"], right_info["y"]

    x_N = x_L + (x_R - x_L) // 2

    y_N = max(y_L + (x_N - x_L), y_R + (x_R - x_N))

    return {"x": x_N, "y": y_N, "type": "node", "left": left_info, "right": right_info, "count": left_info["count"] + right_info["count"]}

  layout = compute_positions(tree, 0)

  max_x = len(leaves) * spacing + 4
  max_y = layout["y"] + 4
  canvas = [[" " for _ in range(max_x)] for _ in range(max_y)]

  def draw(info):
    if info["type"] == "leaf":
      lbl = info["label"]
      x, y = info["x"], info["y"]
      for i, char in enumerate(lbl):
        if x + i < max_x:
          canvas[y][x + i] = char
      return

    x_N, y_N = info["x"], info["y"]
    left, right = info["left"], info["right"]

    draw(left)
    draw(right)

    x_L, y_L = left["x"], left["y"]
    y_diag_left = y_N - (x_N - x_L)
    for y in range(y_L + 1, y_diag_left):
      canvas[y][x_L] = "|"
    for step in range(x_N - x_L):
      canvas[y_diag_left + step][x_L + step] = "\\"

    x_R, y_R = right["x"], right["y"]
    y_diag_right = y_N - (x_R - x_N)
    for y in range(y_R + 1, y_diag_right):
      canvas[y][x_R] = "|"
    for step in range(x_R - x_N):
      canvas[y_diag_right + step][x_R - step] = "/"

    canvas[y_N][x_N] = "V"

  draw(layout)

  # Draw bottom output leg
  root_x, root_y = layout["x"], layout["y"]
  for y in range(root_y + 1, max_y - 1):
    canvas[y][root_x] = "|"

  # Print clean ASCII rendering
  print("\n--- Fusion Tree ASCII Topology ---")
  for row in canvas:
    line = "".join(row).rstrip()
    if line:
      print(line)


if __name__ == "__main__":
  sym = SU2()
  #### \  / / #TODO write a plotter for this.
  ####  \/ /
  ####   \/
  ####    |
  ####
  paper_outer_boundary = {
    -1: [0, 1],
    -2: [0, 1],
    -3: [0, 1],
    -4: [0, 1],
  }

  # Use the new Dataclass architecture
  open_edges = [
    OpenEdge(name=-1, number=1, direction=-1, irreps=[(0, 1), (1, 1)]),
    OpenEdge(name=-2, number=2, direction=-1, irreps=[(0, 1), (1, 1)]),
    OpenEdge(name=-3, number=3, direction=+1, irreps=[(0, 1), (1, 1)]),
    OpenEdge(name=-4, number=4, direction=+1, irreps=[(0, 1), (1, 1)]),
  ]

  internal_edges = [InternalEdge(name="internal_1", number=1)]

  paper_tree = FusionTree(
    open_edges=open_edges,
    internal_edges=internal_edges,
    nodes=[(-1, -2, "internal_1"), ("internal_1", -3, -4)],
    directions=[NodeType.fusion, NodeType.fusion],
    symmetry=sym,
  )

  valid_paper_states = paper_tree.determine_internal_charge_sectors()

  formatted_sectors = []
  for state in valid_paper_states:
    vector = tuple([state["internal_1"], state[-1], state[-2], state[-3], state[-4]])
    formatted_sectors.append(vector)

  paper_tree.listOfChargeSectors = sorted(formatted_sectors)

  paper_tree.listOfDegeneracyTensors = [np.zeros(1) for _ in paper_tree.listOfChargeSectors]

  print(f"Total valid combinations found: {len(paper_tree.listOfChargeSectors)}")
  print("listOfChargeSectors = {")
  for sec in paper_tree.listOfChargeSectors:
    print(f"  {sec},")
  print("}\n")

  print(paper_tree.get_path_between_legs(-1, -3))
  plot_ascii_fusion_tree(paper_tree.nodes)
  paper_tree.fmove("internal_1")
  plot_ascii_fusion_tree(paper_tree.nodes)

  def make_open(edges: list) -> list[OpenEdge]:
    return [OpenEdge(name=e, number=i + 1, direction=-1) for i, e in enumerate(edges)]

  def make_internal(edges: list) -> list[InternalEdge]:
    return [InternalEdge(name=e, number=i + 1) for i, e in enumerate(edges)]

  def make_open_with_charges(edge_charges: dict) -> list[OpenEdge]:
    return [OpenEdge(name=e, number=i + 1, direction=-1, irreps=[(q, 1) for q in charges]) for i, (e, charges) in enumerate(edge_charges.items())]

  outer_charges = {-1: [0, 1 / 2], -2: [0, 1], -3: [0, 1 / 2, 2, 3 / 2]}
  outer_edges = make_open_with_charges(outer_charges)

  tree = FusionTree(
    open_edges=outer_edges,
    internal_edges=[],
    nodes=[(-1, -2, -3)],
    directions=[NodeType.fusion],
    symmetry=sym,
  )

  plot_ascii_fusion_tree(tree.nodes)

  print(tree.determine_internal_charge_sectors())
  print(tree.nodes)
  tree.rmove(0)
  print(tree.determine_internal_charge_sectors())
  print(tree.nodes)  # This is not yet swapped

  plot_ascii_fusion_tree(tree.nodes)
  nodes =  [(-3, -4, 1), (1, 2, -2), (2, -1, -5)]
  # All here are splitting.
  print("#--------------")
  plot_ascii_fusion_tree(nodes)
