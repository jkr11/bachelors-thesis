from abc import ABC, abstractmethod, abstractproperty
from typing import List, Tuple
import numpy as np
from enum import IntEnum
import networkx as nx
import matplotlib.pyplot as plt


class Tensor(ABC):
  """
  Abstract Base Class defining traits for all future tensor types.
  """

  @property
  @abstractmethod
  def rank(self) -> int:
    pass

  @property
  @abstractmethod
  def shape(self) -> Tuple[int, ...]:
    pass

  @abstractmethod
  def transpose(self, axes: Tuple[int, ...]) -> "Tensor":
    pass

  @abstractmethod
  def reshape(self, new_shape: Tuple[int, ...]) -> "Tensor":
    pass

  @abstractmethod
  def permute(self, dims):
    pass

  @abstractmethod
  def conj(self):
    pass

  @abstractmethod
  def contract(self, other: "Tensor", axes: Tuple[List[int], List[int]]) -> "Tensor":
    """maybe name this einsum"""
    pass

  @abstractmethod
  def __add__(self, other: "Tensor"):
    pass

  @abstractmethod
  def __neg__(self):
    pass

  def __sub__(self, other: "Tensor"):
    return self + (-other)

  @abstractmethod
  def __mul__(self, scalar: float) -> "Tensor":
    # TODO: complex?
    pass

  @abstractmethod
  def __matmul__(self, other) -> "Tensor":
    pass

  @staticmethod
  def einsum(equation: str, *operands: "Tensor") -> "Tensor":
    if "->" not in equation:
      pass  # TODO
    input_str, output_labels = equation.split("->")
    input_labels = input_str.split(",")
    pass  # This seems quite hard for now.

  @abstractmethod
  def memory_size(self) -> int:
    raise NotImplementedError("Needs to be implemented for each subclass.")

  def __repr__(self) -> str:
    return f"<{self.__class__.__name__} (rank={self.rank}, shape={self.shape})>"

  @abstractmethod
  def ident(self, k: int) -> "Tensor":
    pass

  @abstractmethod
  def to_numpy(self):
    raise NotImplementedError('Must be implemented in subclass.')


def primitive_einsum(equation, A: Tensor, B: Tensor):
  import math

  lhs, rhs = equation.replace(" ", "").split("->")
  idx_a, idx_b = lhs.split(",")
  idx_out = rhs

  dim_sizes = {}
  for char, size in zip(idx_a, A.shape):
    dim_sizes[char] = size
  for char, size in zip(idx_b, B.shape):
    dim_sizes[char] = size

  contracting = [c for c in idx_a if c in idx_b]
  free_a = [c for c in idx_a if c not in contracting]
  free_b = [c for c in idx_b if c not in contracting]

  perm_a = [idx_a.index(c) for c in (free_a + contracting)]
  A_perm = A.permute(perm_a)

  perm_b = [idx_b.index(c) for c in (contracting + free_b)]
  B_perm = B.permute(perm_b)

  size_free_a = math.prod(dim_sizes[c] for c in free_a)
  size_free_b = math.prod(dim_sizes[c] for c in free_b)
  size_contract = math.prod(dim_sizes[c] for c in contracting)

  A_2d = A_perm.reshape((size_free_a, size_contract))
  B_2d = B_perm.reshape((size_contract, size_free_b))

  out_2d = A_2d @ (B_2d)

  split_shape = tuple(dim_sizes[c] for c in (free_a + free_b))
  out_nd = out_2d.reshape(split_shape)

  current_out_idx = free_a + free_b
  final_perm = [current_out_idx.index(c) for c in idx_out]

  if final_perm != list(range(len(final_perm))):
    out_final = out_nd.permute(final_perm)
  else:
    out_final = out_nd

  return out_final

class NPTensor(Tensor):
  def __init__(self, data: np.ndarray):
    self.data = np.array(data, dtype=complex)

  @property
  def rank(self) -> int:
    return self.data.ndim

  @property
  def shape(self) -> Tuple[int, ...]:
    return self.data.shape

  def transpose(self, axes: Tuple[int, ...]) -> "NPTensor":
    return NPTensor(np.transpose(self.data, axes))

  def reshape(self, new_shape: Tuple[int, ...]) -> "NPTensor":
    return NPTensor(np.reshape(self.data, new_shape))

  def conj(self):
    return NPTensor(np.conj(self.data))

  def contract(self, other, axes: Tuple[List[int], List[int]]) -> "NPTensor":
    if not isinstance(other, NPTensor):
      raise TypeError("Not a dense tensor.")
    res = np.tensordot(self.data, other.data, axes=axes)
    return NPTensor(res)

  def __add__(self, other) -> "NPTensor":
    return NPTensor(self.data + other.data)

  def __neg__(self):
    return NPTensor(-self.data)

  # def __sub__(self, other):
  #   return NPTensor(self.data)

  def __mul__(self, scalar: float) -> "NPTensor":
    return NPTensor(self.data * scalar)

  def __matmul__(self, other):
    return NPTensor(self.data @ other.data)

  def permute(self, dims):
    return NPTensor(np.transpose(self.data, dims))

  def __eq__(self, other):
    return (self.data == other.data).all

  def memory_size(self) -> int:
    return self.data.nbytes  # is this correct?

  def ident(self, k: int):
    return NPTensor(np.identity(k))

  def ndim(self) -> int:
    pass

  @property
  def ndim_open(self) -> int:
    pass

  @property
  def ndim_aux(self) -> int:
    pass

  @property
  def ndim_internal(self) -> int:
    return self.ndim_open + self.ndim_aux - 3

  def __repr__(self):
    str(self.data)

  def __str__(self):
    return str(self.data)

def ident(n:int) -> NPTensor:
  return NPTensor(np.identity(n))

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
from dataclasses import dataclass


@dataclass(frozen=True)
class FusionNode:
  tau: list[str]
  dir: NodeType
  charge: int


class FusionTree:
  def __init__(self, open_edges, internal_edges, nodes, directions):
    self.open_edges = open_edges  # This is a list of (num, dir in {-1,1}, irreps, )
    self.internal_edges = internal_edges  # Same as above but without dir?
    self.nodes = nodes  # List of triples, i.e. [(a,b,c),(c,d,e),(f,e,g),...]
    self.directions: list[NodeType] = (
      directions  # Directions, also triples as above. We should probably fuse this with nodes. Actually, this is the tree type. Then save the actual dirs together with the nodes.
    )
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


def plot_fusion_tree(fusion_tree):
  G = nx.Graph()

  for i, node in enumerate(fusion_tree.nodes):
    node_id = f"v{i}"
    G.add_node(node_id, label=str(fusion_tree.directions[i]))
    for edge_label in node:
      G.add_edge(node_id, f"edge_{edge_label}")

  pos = nx.spring_layout(G)
  nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=1000)
  plt.show()


def run_tests():
  vec1 = NPTensor(np.array([1, 2, 3]))
  vec2 = NPTensor(np.array([4, 5, 6]))
  r_dot = primitive_einsum("i,i->", vec1, vec2)
  expected_dot = np.dot([1, 2, 3], [4, 5, 6])
  print(f"Dot Product Test: {r_dot.data} == {expected_dot}")

  a = NPTensor(np.array([1, 2]))
  b = NPTensor(np.array([3, 4, 5]))
  r_outer = primitive_einsum("i,j->ij", a, b)
  expected_outer = np.outer([1, 2], [3, 4, 5])
  assert np.allclose(r_outer.data, expected_outer)
  print("Outer Product Test: Passed")

  mat = NPTensor(np.random.randn(4, 3))
  vec = NPTensor(np.random.randn(3))
  r_mv = primitive_einsum("ij,j->i", mat, vec)
  expected_mv = mat.data @ vec.data
  assert np.allclose(r_mv.data, expected_mv)
  print("Matrix-Vector Test: Passed")

  A = NPTensor(np.random.randn(3, 5))
  B = NPTensor(np.random.randn(4, 5))
  r_trans = primitive_einsum("ij,kj->ik", A, B)
  expected_trans = A.data @ B.data.T
  print(r_trans.data)
  print(expected_trans)
  assert np.allclose(r_trans.data, expected_trans)
  
  print("Transposed Matmul Test: Passed")

  T1 = NPTensor(np.random.randn(2, 2, 3, 3))
  T2 = NPTensor(np.random.randn(3, 3, 2, 2))
  r_high = primitive_einsum("abjk,jkcd->abcd", T1, T2)

  expected_high = np.einsum("abjk,jkcd->abcd", T1.data, T2.data)
  assert np.allclose(r_high.data, expected_high)
  print("High-Dimensional Fusion Test: Passed")

  mat_diag = NPTensor(np.random.randn(5, 5))
  eye = NPTensor(np.eye(5))
  r_trace = primitive_einsum("ij,ji->", mat_diag, eye)
  expected_trace = np.trace(mat_diag.data)
  assert np.allclose(r_trace.data, expected_trace)
  print(f"Trace Simulation Test: {r_trace.data} == {expected_trace}")

run_tests()


# We can make all of these tests btw, once i redo the project outside of the test repo.
if __name__ == "__main__":
  simpe = FusionTree([], [], [(-1, 1, -3), (-2, 1, -4)], directions=(NodeType.splitting, NodeType.splitting))
  print(determine_type(simpe.nodes, simpe.directions))
  assert simpe.determine_type() == TreeSort.simple
  yoga = FusionTree(
    [f"j{i}" for i in range(1, 7)],
    ["i1", "i2", "i3"],
    [("j1", "j2", "i1"), ("i1", "j4", "i2"), ("i2", "i3", "j3"), ("i3", "j5", "j6")],
    directions=(NodeType.fusion, NodeType.splitting, NodeType.fusion, NodeType.splitting),
  )
  print(yoga.get_node_context("i3"))
  assert yoga.determine_type() == TreeSort.yoga

  testtensor = NPTensor(np.eye(4))
  test2 = testtensor @ testtensor
  assert test2 == testtensor

  test3 = primitive_einsum("ij,jk->ik", testtensor, testtensor)
  print(test3)

  run_tests()
