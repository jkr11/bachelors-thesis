import symmnet.symmetry
from symmnet.symmetry import Symmetry, sector, SU2
from enum import IntEnum
from dataclasses import dataclass
from typing import Any
import matplotlib.pyplot as plt
import networkx as nx

class TreeSort(IntEnum):
  simple = 0
  yoga = 10
  monster = 20


class NodeType(IntEnum):
  splitting = 0
  fusion = 10


# Determine the type for an elementary tree of two nodes, and return their fusion indices.
def determine_elementary_type(taus, dirs) -> tuple[TreeSort, tuple[int, int]]:
  assert len(taus) == 2, "Must be fusion tree from two vertices"
  d0, d1 = dirs[0], dirs[1]
  conn_set = set(taus[0]) & set(taus[1])
  if len(conn_set) != 1:
    raise ValueError(f"Expected 1 connection, found {len(conn_set)}")
  conn = next(iter(conn_set))
  # Since these must be unique, we can use index.
  i1 = taus[0].index(conn)
  i2 = taus[1].index(conn)
  indices = (i1, i2)
  if d0 == d1:  # This needs to be more finely graded now, since we can also construct invalid connections here.
    # I think it is (1,0), (0,1), (2,0), (0,2). But draw them all and do this manually.
    # There is one extra case with fuse, split with (0,1) connection that can be simple, so this is defined below.
    return TreeSort.simple, indices
  if d0 == NodeType.fusion and d1 == NodeType.splitting:
    if indices == (0, 1) or indices == (2, 0):  # TODO: really check if this is right.
      return TreeSort.simple, indices
    return TreeSort.yoga, indices
  else:
    lookup = {
      (1, 2): TreeSort.yoga,
      (2, 0): TreeSort.yoga,
      (1, 0): TreeSort.monster,
      (2, 1): TreeSort.monster,  # TODO... expand.
    }
    result = lookup.get(indices)
    if result:
      return result, indices
  raise NotImplementedError(f"Unhandled configuration: {d0}-{d1} with indices {indices}")


# There are (2,2),(2,1),(2,0),(1,2),(0,2),(0,1),(1,0),(0,0)


def fmove_basic_simple(taus, dirs):  # Does it make sense to implement a type for the basis trees?
  # i guess we can just use Table 1 in the programming guide for this. Leaving this out of the class in case we get the sort info already passed from toplevel. The thesis by schmoll has more of these tabulated, i.e. for yoga moves as well (i believe its 16?)
  # Well and now we have to make determine type also return the ids.
  assert len(taus) == 2
  treetype, order = determine_elementary_type(taus, dirs)
  a, b, c = taus[0]
  d, e, f = taus[1]
  if treetype == TreeSort.simple:
    if order == (0, 2):
      return [(a, d, b)]


# NOTE: Since we maybe want this labeled, consider both the options of having this as Captial letters + any numstr for the externals and lowercase for the internals or like in the paper pos and negative for outer and inner.
# TODO: Is a new structure for node usable? So we dont have to handle multiple properties at the same time. But then again we still have the outer and inner arrays. What to do there?

# @dataclass
# class Edge:
#  edgeNumber : int|str
#  edgeDirection : int
#  edgeIrreps: list[sector]
#
# @dataclass(frozen=True)
# class FusionNode:
#  tau: list[str|int] # These are the edge nums.
#  dir: NodeType
#  charge: int

# Devise a new class here  that would look like FusionTree(domain, codomain, internal, multiplicities, directions, etc...)


class FusionTree:
  """
  The basic blocks of the fusion tree are trivalent vertices, that look as follows
       c
       |  (Outgoing leg)
       |
       * <-- Multiplicity index α ∈ {1, 2, ..., N_ab^c}
      / \
     /   \
    a     b  (Incoming legs)
  """

  def __init__(self, open_edges, internal_edges, nodes, directions, symmetry: Symmetry = SU2()):
    # Discuss if we want this as domain and codomain
    self.open_edges = open_edges  # This is a list of (num, dir in {-1,1}, irreps, )
    self.internal_edges = internal_edges  # Same as above but without dir?
    self.nodes = nodes  # List of triples, i.e. [(a,b,c),(c,d,e),(f,e,g),...]
    self.directions: list[NodeType] = list(directions)  # orientation of each node, i.e. "fusion" or "splitting"
    self.multiplicities:list[int]
    self.symmetry = symmetry
    self._verify()

  def _verify(self):
    assert all(len(node) == 3 for node in self.nodes), "Tree not made of tau triples"
    assert len(self.nodes) == len(self.directions), "Directions not given for every node."
    # assert len(self.internal_edges) == len(self.open_edges) - 3
    # This is not actuallly true in general.

  def plot(self, ax=None, show=True, layout="spring"):
    return plot_fusion_tree(self, ax=ax, show=show, layout=layout)

  def get_node_context(self, edge_id: int | str):
    assert edge_id in self.internal_edges
    node_indices = [i for i, node in enumerate(self.nodes) if edge_id in node]
    if len(node_indices) < 2:
      raise ValueError(f"Edge {edge_id} does not link 2 internal vertices.")
    return (
      (self.nodes[node_indices[0]], self.nodes[node_indices[1]]),
      (self.directions[node_indices[0]], self.directions[node_indices[1]]),
    )

  def determine_type(self) -> TreeSort:
    found_types = {determine_elementary_type(*self.get_node_context(edge))[0] for edge in self.internal_edges}

    if TreeSort.monster in found_types:
      return TreeSort.monster
    if TreeSort.yoga in found_types:
      return TreeSort.yoga

    return TreeSort.simple

  def _legs_share_node(self, leg1, leg2):
    for node in self.nodes:
      if leg1 in node and leg2 in node:
        return True
    return False

  def _resolve_identity_nodes(self):
    for inner in self.internal_edges:
      taus, _ = self.get_node_context(inner)
      t0, t1 = taus[0], taus[1]
      print(t0)
      print(t1)

  def fmove(self, edge):
    # This one is a bit strange because we only have split split and fuse fuse right, but in one of the theses here there was a full table of fmoves.
    taus, dirs = self.get_node_context(edge)
    print(taus)
    sort, (i1, i2) = determine_elementary_type(taus, dirs)
    a, b, c = taus[0]
    d, e, f = taus[1]
    d0, d1 = dirs[0], dirs[1]
    new_dirs = [d0, d1]
    if sort == TreeSort.simple:
      if d0 == d1 == NodeType.fusion:
        if (i1, i2) == (1, 2):
          new_taus = [(a, d, b), (b, e, c)]
          # Just as an example here, this would then have the fmove
          # F_(adec)^((b=f))
        elif (i1, i2) == (2, 0):
          new_taus = [(a, c, f), (b, e, c)]
        # elif (i1, i2) == (2,1):

        else:
          raise NotImplementedError("FMove is not yet fully implemente.")
      elif d0 == d1 == NodeType.splitting:
        if (i1, i2) == (2, 0):
          new_taus = [(a, c, f), (c, b, e)]
        elif (i1, i2) == (1, 0):
          new_taus = [(a, e, b), (b, f, c)]
        else:
          raise NotImplementedError(f"FMove is not yet impelemneted fully, {i1, i2}")
    elif sort == TreeSort.yoga:
      if d0 == NodeType.splitting and d1 == NodeType.fusion:
        # (-1, -3, 1) (1, -2, -3)
        if (i1, i2) == (2, 0):
          new_taus = [(a, e, c), (c, b, f)]
          new_dirs = [NodeType.fusion, NodeType.splitting]
        elif (i1, i2) == (1, 0):
          new_taus = [(a, e, b), (b, f, c)]
          new_dirs = [NodeType.fusion, NodeType.splitting]
        elif (i1, i2) == (2, 1):
          new_taus = [(d, a, c), (c, b, f)]
          new_dirs = [NodeType.fusion, NodeType.splitting]
        else:
          raise NotImplementedError("SplitFuse cases not implemented")
      elif d0 == NodeType.fusion and d1 == NodeType.splitting:
        if (i1, i2) == (2, 0):
          new_taus = [(a, c, f), (c, b, e)]
          new_dirs = [NodeType.splitting, NodeType.fusion]
        else:
          raise NotImplementedError(f"Fuse-Split case {(i1, i2)} not implemented")
    else:
      raise NotImplementedError("Error in case ")
    # This can be done better? write something like context for htis?
    node_indices = [idx for idx, node in enumerate(self.nodes) if edge in node]
    self.nodes[node_indices[0]] = new_taus[0]
    self.nodes[node_indices[1]] = new_taus[1]

    self.directions[node_indices[0]] = new_dirs[0]
    self.directions[node_indices[1]] = new_dirs[1]

  def permutation(self, swap_sequence: list[tuple[int, int]]):
    for i, j in swap_sequence:
      pass

  def swap(a, b):
    pass

  # Attempt two at this.
  def determine_internal_charge_sectors_passes(self, outer_charges: dict[Any, list[Any]]):
    forward_sets: dict[Any, set[Any]] = {}

    for edge in self.open_edges:
      if edge in outer_charges:
        forward_sets[edge] = set(outer_charges[edge])
      else:
        raise ValueError(f"Required open edge '{edge}' is missing.")

    all_edges = {e for node in self.nodes for e in node}
    changed = True

    while changed and len(forward_sets) < len(all_edges):
      changed = False
      for node, ntype in zip(self.nodes, self.directions):
        if ntype == NodeType.fusion:
          c1, c2, parent = node
          if c1 in forward_sets and c2 in forward_sets and parent not in forward_sets:
            possible = set()
            for q1 in forward_sets[c1]:
              for q2 in forward_sets[c2]:
                possible.update(self.symmetry.possible_charge_sectors(q1, q2))
            forward_sets[parent] = possible
            changed = True
        elif ntype == NodeType.splitting:
          parent, c1, c2 = node
          if parent in forward_sets and (c1 not in forward_sets or c2 not in forward_sets):
            pass

    backward_sets: dict[Any, set[Any]] = {e: set(forward_sets[e]) for e in forward_sets}

    for node, ntype in reversed(list(zip(self.nodes, self.directions))):
      if ntype == NodeType.fusion:
        c1, c2, parent = node
        valid_c1, valid_c2 = set(), set()
        for q1 in backward_sets[c1]:
          for q2 in backward_sets[c2]:
            overlap = set(self.symmetry.possible_charge_sectors(q1, q2)) & backward_sets[parent]
            if overlap:
              valid_c1.add(q1)
              valid_c2.add(q2)
        backward_sets[c1] &= valid_c1
        backward_sets[c2] &= valid_c2

    import itertools

    # sorted_edges = sorted(list(all_edges), key=lambda x: str(x))

    valid_configurations = []
    keys = list(backward_sets.keys())
    ranges = [backward_sets[k] for k in keys]

    for combo in itertools.product(*ranges):
      assignment = dict(zip(keys, combo))
      is_valid = True
      for node in self.nodes:
        if not self.symmetry.is_valid(assignment[node[0]], assignment[node[1]], assignment[node[2]]):
          is_valid = False
          break
      if is_valid:
        valid_configurations.append(assignment)

    return valid_configurations

  # I dont like this method here, maybe we can do this better.
  def determine_internal_charge_sectors(self, outer_charges: dict[Any, list[tuple[Any, int]]]):
    all_edges = set()
    for node in self.nodes:
      all_edges.update(node)
    # print(f"All edges: {all_edges}")

    # TODO: remove
    normalized_outer = {}
    degen_lookup = {}
    for e in self.open_edges:
      if e in outer_charges:
        v = outer_charges[e]
        normalized_outer[e] = list(v) if isinstance(v, (list, tuple, set, range)) else [v]
      else:
        raise ValueError(f"Required open edge '{e}' is missing from the outer charges input.")
    # print(f"Normalized outer: {normalized_outer}")
    valid_configurations = []

    def backtrack(assignments):
      # Prune early if any node violates
      for node in self.nodes:
        if all(e in assignments for e in node):
          if not self.symmetry.is_valid(assignments[node[0]], assignments[node[1]], assignments[node[2]]):
            return

      # All edges are handeled
      if len(assignments) == len(all_edges):
        valid_configurations.append(assignments.copy())
        return

      # establish boundary conditions? Unnecessary?
      unassigned_open = [e for e in self.open_edges if e not in assignments]
      # print(unassigned_open)
      if unassigned_open:
        next_edge = unassigned_open[0]
        for val in normalized_outer[next_edge]:
          assignments[next_edge] = val
          backtrack(assignments)
          del assignments[next_edge]
        return

      # Propaagate over all nodes wherethere are exactly 2 nodes known and resolve them.
      for node in self.nodes:
        known_edges = [e for e in node if e in assignments]
        if len(known_edges) == 2:
          unknown_edges = [e for e in node if e not in assignments]
          if unknown_edges:
            unknown_edge = unknown_edges[0]
            charge_a = assignments[known_edges[0]]
            charge_b = assignments[known_edges[1]]

            candidates = self.symmetry.possible_charge_sectors(charge_a, charge_b)
            for candidate in candidates:
              assignments[unknown_edge] = candidate
              backtrack(assignments)
              del assignments[unknown_edge]
            return

      raise ValueError("Tree cannot be uniquely proped.")

    backtrack({})
    return valid_configurations


def plot_fusion_tree(fusion_tree, ax=None, show=True, layout="spring"):
  if plt is None:
    raise ImportError("matplotlib is required to plot fusion trees")

  if ax is None:
    ax = plt.subplots(figsize=(7, 6))[1]

  node_ids = [f"v{i}" for i in range(len(fusion_tree.nodes))]
  edge_ids = [f"e_{edge}" for edge in sorted({edge for node in fusion_tree.nodes for edge in node}, key=str)]
  node_labels = {node_id: f"{fusion_tree.directions[i].name}\n{i}" for i, node_id in enumerate(node_ids)}
  edge_labels = {edge_id: edge_id[2:] for edge_id in edge_ids}

  if nx is not None:
    G = nx.Graph()
    for node_id in node_ids:
      G.add_node(node_id, kind="vertex")
    for edge_id in edge_ids:
      G.add_node(edge_id, kind="edge")
    for node_id, node in zip(node_ids, fusion_tree.nodes):
      for edge in node:
        edge_id = f"e_{edge}"
        G.add_edge(node_id, edge_id)

    pos = nx.spring_layout(G, seed=0)
    vertex_nodes = [n for n, d in G.nodes(data=True) if d["kind"] == "vertex"]
    edge_nodes = [n for n, d in G.nodes(data=True) if d["kind"] == "edge"]
    nx.draw_networkx_nodes(G, pos, nodelist=vertex_nodes, node_color="skyblue", node_size=700, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=edge_nodes, node_color="lightgreen", node_size=300, ax=ax)
    nx.draw_networkx_edges(G, pos, ax=ax)
    nx.draw_networkx_labels(G, pos, labels={**node_labels, **edge_labels}, font_size=9, ax=ax)
  else:
    positions = {}
    for i, node_id in enumerate(node_ids):
      positions[node_id] = (0.0, -i)
    for j, edge_id in enumerate(edge_ids):
      positions[edge_id] = ((-1.5 if j % 2 == 0 else 1.5), -j * 0.75)

    for node_id, node in zip(node_ids, fusion_tree.nodes):
      for edge in node:
        edge_id = f"e_{edge}"
        x0, y0 = positions[node_id]
        x1, y1 = positions[edge_id]
        ax.plot([x0, x1], [y0, y1], color="black", linewidth=1)

    for node_id in node_ids:
      x, y = positions[node_id]
      ax.scatter([x], [y], s=700, color="skyblue", zorder=3)
      ax.text(x, y, node_labels[node_id], ha="center", va="center", fontsize=9)
    for edge_id in edge_ids:
      x, y = positions[edge_id]
      ax.scatter([x], [y], s=300, color="lightgreen", zorder=3)
      ax.text(x, y, edge_labels[edge_id], ha="center", va="center", fontsize=8)

  ax.set_axis_off()
  if show:
    plt.show()
  return ax


if __name__ == "__main__":
  sym = symmnet.symmetry.SU2()

  paper_outer_boundary = {
    -1: [0, 1],  # j1
    -2: [0, 1],  # j2
    -3: [0, 1],  # j3
    -4: [0, 1],  # j4
  }

  paper_tree = FusionTree(
    open_edges=[-1, -2, -3, -4],
    internal_edges=["internal_1"],
    nodes=[(-1, -2, "internal_1"), ("internal_1", -3, -4)],
    directions=(NodeType.fusion, NodeType.fusion),
    symmetry=sym,
  )

  valid_paper_states = paper_tree.determine_internal_charge_sectors(paper_outer_boundary)

  # Formatting to match 4.6
  formatted_sectors = []
  for state in valid_paper_states:
    vector = [state["internal_1"], state[-1], state[-2], state[-3], state[-4]]
    formatted_sectors.append(vector)

  formatted_sectors.sort()
  print(f"Total valid combinations found: {len(formatted_sectors)}")
  print("listOfChargeSectors = {")
  for sec in formatted_sectors:
    print(f"  {sec},")
  print("}\n")


  paper_tree.plot()

# def plot_fusion_tree(fusion_tree):
#  G = nx.Graph()
#
#  for i, node in enumerate(fusion_tree.nodes):
#    node_id = f"v{i}"
#    G.add_node(node_id, label=str(fusion_tree.directions[i]))
#    for edge_label in node:
#      G.add_edge(node_id, f"edge_{edge_label}")
#
#  pos = nx.spring_layout(G)
#  nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=1000)
#  plt.show()


# We can make all of these tests btw, once i redo the project outside of the test repo.
# if __name__ == "__main__":
#  simpe = FusionTree([], [], [(-1, 1, -3), (-2, 1, -4)], directions=(NodeType.splitting, NodeType.splitting))
#  print(determine_type(simpe.nodes, simpe.directions))
#  assert simpe.determine_type() == TreeSort.simple
#  yoga = FusionTree(
#    [(f"j{i}", [0,1], -1) for i in range(1, 7)],
#    [(f"i{i}", []) for i in range(1,3)],
#    [("j1", "j2", "i1"), ("i1", "j4", "i2"), ("i2", "i3", "j3"), ("i3", "j5", "j6")],
#    directions=(NodeType.fusion, NodeType.splitting, NodeType.fusion, NodeType.splitting),
#  )
#  print(yoga.get_node_context("i3"))
#  assert yoga.determine_type() == TreeSort.yoga
