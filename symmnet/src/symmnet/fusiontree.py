from enum import IntEnum
from dataclasses import dataclass

class TreeSort(IntEnum):
  simple = 0
  yoga = 10
  monster = 20

class NodeType(IntEnum):
  splitting = 0
  fusion = 10

# Determine the type for an elementary tree of two nodes, and return their fusion indices.
def determine_type(taus, dirs) -> tuple[TreeSort, tuple[int, int]]:
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
  treetype, order = determine_type(taus, dirs)
  a, b, c = taus[0]
  d, e, f = taus[1]
  if treetype == TreeSort.simple:
    if order == (0, 2):
      return [(a, d, b)]


# NOTE: Since we maybe want this labeled, consider both the options of having this as Captial letters + any numstr for the externals and lowercase for the internals or like in the paper pos and negative for outer and inner.
# TODO: Is a new structure for node usable? So we dont have to handle multiple properties at the same time. But then again we still have the outer and inner arrays. What to do there?


@dataclass(frozen=True)
class FusionNode:
  tau: list[str]
  dir: NodeType
  charge: int

@dataclass
class Edge:
  edgeNumber : int|str
  edgeDirection : int
  edgeIrreps: list[int]
  # isFused


class FusionTree:
  def __init__(self, open_edges, internal_edges, nodes, directions):
    self.open_edges = open_edges  # This is a list of (num, dir in {-1,1}, irreps, )
    self.internal_edges = internal_edges  # Same as above but without dir?
    self.nodes = nodes  # List of triples, i.e. [(a,b,c),(c,d,e),(f,e,g),...]
    self.directions: list[NodeType] = (
      directions  # Directions, also triples as above. We should probably fuse this with nodes. Actually, this is the tree type. Then save the actual dirs together with the nodes.
    )
    self.open_edges_2 : list[Edge]
    self.internal_edges_2 : list[Edge]
    self._verify()

  def _verify(self):
    assert all(len(node) == 3 for node in self.nodes), "Tree not made of tau triples"
    assert len(self.nodes) == len(self.directions), "Directions not given for every node."

  def get_node_context(self, node_id: int | str):
    # Get the edges context by finding the two nodes it connects. TODO: rename.
    # Also, what happens if we target a leaf
    assert node_id in self.internal_edges
    node_indices = [i for i, node in enumerate(self.nodes) if node_id in node]
    return ((self.nodes[node_indices[0]], self.nodes[node_indices[1]]), (self.directions[node_indices[0]], self.directions[node_indices[1]]))

  def determine_type(self) -> TreeSort:
    # Here we need sme kind of iterator that gives us elementary subtrees.
    # Every internal edge has 4 adjacent edges (without loops?)
    found_types = {determine_type(*self.get_node_context(edge))[0] for edge in self.internal_edges}

    # Is the fallthrough correct here? It has to be, since we consider connecting nodes.
    if TreeSort.monster in found_types:
      return TreeSort.monster
    if TreeSort.yoga in found_types:
      return TreeSort.yoga

    return TreeSort.simple

  def get_valid_sectors(self):
    edge_options = {}
    for edge in self.open_edges_2:
      edge_options[edge.edgeNumber] = edge.edgeIrreps

  def calculate_internal_sectors(self):
    all_edges = {e for t in self.nodes for e in t}


#def plot_fusion_tree(fusion_tree):
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
if __name__ == "__main__":
  simpe = FusionTree([], [], [(-1, 1, -3), (-2, 1, -4)], directions=(NodeType.splitting, NodeType.splitting))
  print(determine_type(simpe.nodes, simpe.directions))
  assert simpe.determine_type() == TreeSort.simple
  yoga = FusionTree(
    [(f"j{i}", [0,1], -1) for i in range(1, 7)],
    ["i1", "i2", "i3"],
    [("j1", "j2", "i1"), ("i1", "j4", "i2"), ("i2", "i3", "j3"), ("i3", "j5", "j6")],
    directions=(NodeType.fusion, NodeType.splitting, NodeType.fusion, NodeType.splitting),
  )
  print(yoga.get_node_context("i3"))
  assert yoga.determine_type() == TreeSort.yoga

