from dataclasses import dataclass
from typing import Optional, Any
from enum import IntEnum


class NodeType(IntEnum):
  splitting = 0
  fusion = 10


class TreeSort(IntEnum):
  simple = 0
  yoga = 10
  monster = 2


@dataclass
class Edge:
  num: int  # label
  direction: int
  irreps: Any


@dataclass
class Node:
  edges: tuple[Edge, Edge, Edge]
  _type: NodeType
  multiplicity: Optional[int] = 1

def determine_type(node1: Node, node2: Node):
  d0 = node1._type
  d1 = node2._type
  connection = next(iter(set(node1.edges) & set(node2.edges)))
  i1 = node1.edges.index(connection)
  i2 = node2.edges.index(connection)
  indices = (i1, i2)
  if d0 == d1:
    return TreeSort.simple, indices
  if d0 == NodeType.fusion and d1 == NodeType.splitting:
    if indices == (0, 1) or indices == (2, 0):
      return TreeSort.simple, indices
    return TreeSort.yoga, indices
  else:
    lookup = {
      (1, 2): TreeSort.yoga,
      (2, 0): TreeSort.yoga,
      (1, 0): TreeSort.monster,
      (2, 1): TreeSort.monster,
    }
    result = lookup.get(indices)
    if result:
      return result, indices
  raise NotImplementedError(f"Unhandled configuration: {d0}-{d1} with indices {indices}")

# TODO... expand.
class FusionTree:
  open_edges: list[Edge]
  internal_edges: list[Edge]
  nodes: list[Node]
  symmetry: Any

  def __init__(self, open_edges, internal_edges, nodes, symmetry: Any):
    self.open_edges = list(open_edges)
    self.internal_edges = list(internal_edges)
    self.nodes = [Node(*node) for node in nodes]
    self.symmetry = symmetry
    self._verify()

  def _verify(self):
    assert all(len(node.edges) == 3 for node in self.nodes), "Tree not made of tau triples"

  def reduce_bubble(self, n1:Node, n2:Node):
    shared = set(n1.edges) & set(n2.edges)
    exts = set(n1.edges) ^ set(n2.edges)
    

