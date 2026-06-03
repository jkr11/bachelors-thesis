from dataclasses import dataclass, field
from typing import Optional, Any

@dataclass
class Edge:
    num: int # label
    direction: int  # -1 for incoming, 1 for outgoing
    irreps: Any

@dataclass
class Node:
    edges: tuple[Edge,Edge, Edge]
    node_type: str  # "fusion" or "splitting"
    multiplicity: Optional[int] = 1

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
    