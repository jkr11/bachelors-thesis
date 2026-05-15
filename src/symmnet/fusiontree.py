import symmnet.symmetry
from symmnet.symmetry import Symmetry, sector, SU2
from enum import IntEnum
from dataclasses import dataclass
from typing import Any


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
  if d0 == d1:  # This needs to be more fiely graded now, since we can also construct invalid connections here.
    # I think it is (1,0), (0,1), (2,0), (0,2). But draw them all and do this manually.
    # There is one extra case with fuse, split with (0,1) connection that can be simple, so this is defined below.
    return TreeSort.simple, indices
  if d0 == NodeType.fusion and d1 == NodeType.splitting:
    if indices == (0, 1):
      return TreeSort.simple, indices
    return TreeSort.yoga, indices
  else:
    lookup = {
      (1, 2): TreeSort.yoga,
      (2, 0): TreeSort.yoga,
      (1, 0): TreeSort.monster,
      (2, 2): TreeSort.monster,
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


class FusionTree:
  def __init__(self, open_edges, internal_edges, nodes, directions, symmetry: Symmetry = SU2()):
    self.open_edges = open_edges  # This is a list of (num, dir in {-1,1}, irreps, )
    self.internal_edges = internal_edges  # Same as above but without dir?
    self.nodes = nodes  # List of triples, i.e. [(a,b,c),(c,d,e),(f,e,g),...]
    self.directions: list[NodeType] = directions  # orientation of each node, i.e. "fusion" or "splitting"
    self.symmetry = symmetry
    self._verify()

  def _verify(self):
    assert all(len(node) == 3 for node in self.nodes), "Tree not made of tau triples"
    assert len(self.nodes) == len(self.directions), "Directions not given for every node."

  def get_node_context(self, node_id: int | str):
    # Get the edges context by finding the two nodes it connects. TODO: rename.
    # Also, what happens if we target a leaf
    # assert node_id in self.internal_edges
    node_indices = [i for i, node in enumerate(self.nodes) if node_id in node]
    if len(node_indices) < 2:
      raise ValueError(f"Edge {node_id} does not link 2 internal vertices.")
    return (
      (self.nodes[node_indices[0]], self.nodes[node_indices[1]]),
      (self.directions[node_indices[0]], self.directions[node_indices[1]]),
    )

  def determine_type(self) -> TreeSort:
    # Here we need sme kind of iterator that gives us elementary subtrees.
    # Every internal edge has 4 adjacent edges (without loops?)
    found_types = {determine_elementary_type(*self.get_node_context(edge))[0] for edge in self.internal_edges}

    # Is the fallthrough correct here? It has to be, since we consider connecting nodes.
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

  def fmove(self, edge):
    # This one is a bit strange because we only have split split and fuse fuse right, but in one of the theses here there was a full table of fmoves.
    taus, dirs = self.get_node_context(edge)
    print(taus)
    sort, (i1,i2) = determine_elementary_type(taus, dirs)
    a,b,c = taus[0]
    d,e,f = taus[1]
    d0,d1 = dirs[0],dirs[1]
    if sort == TreeSort.simple:
      if d0 == d1 == NodeType.fusion:
        if (i1,i2) == (1,2):
          new_taus = [(a,b,d),(b,e,c)]
        elif (i1,i2) == (2,0):
          new_taus = [(a,c,f),(b,e,c)]
        else:
          raise NotImplementedError("FMove is not yet fully implemente.")
      elif d0 == d1 == NodeType.splitting:
        if (i1,i2) == (2,0):
          new_taus = [(a,c,f),(c,b,e)]
        elif (i1,i2) == (1,0):
          new_taus = [(a,e,b),(b,f,c)]
        else: raise NotImplementedError(f"FMove is not yet impelemneted fully, {i1, i2}")
      else: raise NotImplementedError('SplitFuse cases not implemented')
    else:
      raise NotImplementedError("Yoga not yet impelemnet.")
    # This can be done better? write something like context for htis?
    node_indices = [idx for idx, node in enumerate(self.nodes) if edge in node]
    self.nodes[node_indices[0]] = new_taus[0]
    self.nodes[node_indices[1]] = new_taus[1]

  def permutation(self, swap_sequence:list[tuple[int,int]]):
    for i,j in swap_sequence:
      pass

  def swap(a, b):
    pass

  def determine_internal_charge_sectors(self, outer_charges: dict[Any, Any]):
    all_edges = set()
    for node in self.nodes:
      all_edges.update(node)
    # print(f"All edges: {all_edges}")

    # TODO: remove
    normalized_outer = {}
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

      # establish boundary conditions? Unecessary?
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
