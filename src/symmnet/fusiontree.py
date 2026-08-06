import symmnet.symmetry
from symmnet.symmetry import Symmetry, sector, SU2
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Any
import numpy as np


class TreeSort(IntEnum):
  simple = 0
  yoga = 10
  monster = 20


class NodeType(IntEnum):
  splitting = 0
  fusion = 10


type label = int | str


@dataclass
class OpenEdge:
  name: label
  number: int  # TODO what is this
  direction: int  # (-1 or 1)
  irreps: list[tuple[sector, int]] = field(default_factory=list)  # (ji, tji)
  is_fused: bool = False  # TODO
  original_irreps: list[Any] = field(default_factory=list)  # TODO


@dataclass
class InternalEdge:
  name: label
  number: int
  irreps: list[tuple[sector, int]] = field(default_factory=list)


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


class FusionTree:
  def __init__(
    self,
    open_edges: list[OpenEdge],
    internal_edges: list[InternalEdge],
    nodes: list[tuple[label, label, label]],
    directions: list[NodeType],
    symmetry: Symmetry = SU2(),
  ):
    # Discuss if we want this as domain and codomain
    self.open_edges = open_edges  # This is a list of (num, dir in {-1,1}, irreps, )
    self.internal_edges = internal_edges  # Same as above but without dir?
    self.nodes = nodes  # List of triples, i.e. [(a,b,c),(c,d,e),(f,e,g),...]
    self.directions: list[NodeType] = list(directions)  # orientation of each node, i.e. "fusion" or "splitting"
    # self.multiplicities: list[int]
    self.symmetry = symmetry

    self.listOfChargeSectors: list[tuple[Any, ...]] = []
    self.listOfDegeneracyTensors: list[np.ndarray] = []
    self._verify()

  def _verify(self):
    assert all(len(node) == 3 for node in self.nodes), "Tree not made of tau triples"
    assert len(self.nodes) == len(self.directions), "Directions not given for every node."

  def _get_open_names(self) -> list[label]:
    return [e.name for e in self.open_edges]

  def _get_internal_names(self) -> list[label]:
    return [e.name for e in self.internal_edges]

  def get_node_context(self, edge_id: label):
    assert edge_id in self._get_internal_names()
    node_indices = [i for i, node in enumerate(self.nodes) if edge_id in node]
    if len(node_indices) < 2:
      raise ValueError(f"Edge {edge_id} does not link 2 internal vertices.")
    return (
      (self.nodes[node_indices[0]], self.nodes[node_indices[1]]),
      (self.directions[node_indices[0]], self.directions[node_indices[1]]),
    )

  def determine_type(self) -> TreeSort:
    found_types = {determine_elementary_type(*self.get_node_context(edge))[0] for edge in self._get_internal_names()}

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

  def fmove(self, edge: label):
    # This one is a bit strange because we only have split split and fuse fuse right, but in one of the theses here there was a full table of fmoves.
    taus, dirs = self.get_node_context(edge)
    print(taus)
    sort, (i1, i2) = determine_elementary_type(taus, dirs)
    a, b, c = taus[0]
    d, e, f = taus[1]
    d0, d1 = dirs[0], dirs[1]
    new_dirs = [d0, d1]
    new_taus = None
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
    assert new_taus is not None
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
  def _determine_internal_charge_sectors(self, outer_charges: dict[Any, list[Any]]):
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

  def determine_internal_charge_sectors(self, outer_charges: dict[Any, list[Any]]):
    forward_sets: dict[Any, set[Any]] = {}

    open_names = self._get_open_names()
    for edge in open_names:
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
            pass  # To implement

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


if __name__ == "__main__":
  sym = symmnet.symmetry.SU2()

  paper_outer_boundary = {
    -1: [0, 1],
    -2: [0, 1],
    -3: [0, 1],
    -4: [0, 1],
  }

  # Use the new Dataclass architecture
  open_edges = [
    OpenEdge(name=-1, number=1, direction=-1),
    OpenEdge(name=-2, number=2, direction=-1),
    OpenEdge(name=-3, number=3, direction=+1),
    OpenEdge(name=-4, number=4, direction=+1),
  ]

  internal_edges = [InternalEdge(name="internal_1", number=1)]

  paper_tree = FusionTree(
    open_edges=open_edges,
    internal_edges=internal_edges,
    nodes=[(-1, -2, "internal_1"), ("internal_1", -3, -4)],
    directions=[NodeType.fusion, NodeType.fusion],
    symmetry=sym,
  )

  valid_paper_states = paper_tree.determine_internal_charge_sectors(paper_outer_boundary)

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
