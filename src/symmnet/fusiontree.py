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
    self._verify()

  def _verify(self):
    assert all(len(node) == 3 for node in self.nodes), "Tree not made of tau triples"
    assert len(self.nodes) == len(self.directions), "Directions not given for every node."

  def _get_open_names(self) -> list[label]:
    return [e.name for e in self.open_edges]

  def _get_internal_names(self) -> list[label]:
    return [e.name for e in self.internal_edges]

  def __str__(self):
    node_str = " ".join([f"[{node}| {dir}]" for node, dir in zip(self.nodes, self.directions)])

    leg_str = " ".join([f"{e.name} : {e.irreps}" for e in self.open_edges])

    return leg_str + "\n" + node_str

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
    # print(taus) #TODO
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

  def get_path_between_legs(self, leg1: label, leg2: label) -> list[label]:
    from collections import deque

    if leg1 == leg2:
      return []

    start_nodes = [i for i, node in enumerate(self.nodes) if leg1 in node]
    target_nodes = [i for i, node in enumerate(self.nodes) if leg2 in node]
    if not start_nodes or not target_nodes:
      raise ValueError(f"One or both legs ({leg1}, {leg2}) not found")

    start_idx = start_nodes[0]
    target_idx = target_nodes[0]

    if start_idx == target_idx:
      return []  # Both legs share same node

    internal_names = set(self._get_internal_names())

    # (current_node_index, path_of_internal_edge_ids)
    queue = deque([(start_idx, [])])
    visited = {start_idx}
    while queue:
      curr_idx, path = queue.popleft()
      if curr_idx == target_idx:
        return path
      curr_node = self.nodes[curr_idx]
      for edge_id in curr_node:
        if edge_id in internal_names:
          for neighbor_idx, neighbor_node in enumerate(self.nodes):
            if neighbor_idx not in visited and edge_id in neighbor_node:
              visited.add(neighbor_idx)
              queue.append((neighbor_idx, path + [edge_id]))
    raise RuntimeError(f"No connected path between '{leg1}' and '{leg2}'.")

  def get_parent_node(self, leg1: label, leg2: label) -> int:
    for idx, node in enumerate(self.nodes):
      if leg1 in node and leg2 in node:
        return idx
    raise ValueError(f"'{leg1}' and '{leg2}' do not share a common node.")

  def rmove(self, node_id: int):
    node = self.nodes[node_id]
    self.nodes[node_id] = (node[1], node[0], node[2])

  def _wrap_with_dummy(self, leg_a: label, leg_b: label, direction: NodeType) -> label:
    dummy_name = f"__dummy_vacuum_{leg_a}_{leg_b}__"
    max_num = max((e.number for e in self.open_edges + self.internal_edges), default=0)
    dummy_edge = OpenEdge(
      name=dummy_name,
      number=max_num + 1,
      direction=1,
      irreps=[(0, 1)],
      is_fused=False,
    )
    self.open_edges.append(dummy_edge)
    if direction == NodeType.fusion:
      new_node = (leg_a, dummy_name, leg_b)
    else:
      new_node = (leg_b, leg_a, dummy_name)
    self.nodes.append(new_node)
    self.directions.append(direction)
    return dummy_name

  def _fuse_irreps(self, irreps1, irreps2) -> list[tuple[Any, int]]:  # TODO: implement symmetry abc as the grothendieck ring
    fused: dict[Any, int] = {}
    for j1, d1 in irreps1:
      for j2, d2 in irreps2:
        for f in self.symmetry.possible_charge_sectors(j1, j2):
          fused[f] = fused.get(f, 0) + d1 * d2
    return sorted(fused.items())

  def fuse_legs(self, leg1: label, leg2: label, new_name: label | None = None) -> tuple[OpenEdge, label, bool]:
    if not self._legs_share_node(leg1, leg2):
      for internal_edge in self.get_path_between_legs(leg1, leg2):
        self.fmove(internal_edge)

    try:
      node_idx = self.get_parent_node(leg1, leg2)
    except ValueError:
      raise ValueError(f"{leg1!r} and {leg2!r} do not share lges") from None

    node = self.nodes[node_idx]
    direction = self.directions[node_idx]

    if direction == NodeType.fusion:
      c1, c2, parent = node
    else:
      parent, c1, c2 = node  # TODO rem

    edge1 = next(e for e in self.open_edges if e.name == leg1)
    edge2 = next(e for e in self.open_edges if e.name == leg2)
    fused_irreps = self._fuse_irreps(edge1.irreps, edge2.irreps)

    parent_edge = next((e for e in self.open_edges if e.name == parent), None)
    parent_was_internal = parent_edge is None

    if parent_was_internal:
      fused_name = parent if new_name is None else new_name
    else:
      if new_name is None:
        raise ValueError(f"{parent!r} is already used..")
      fused_name = new_name

    self.nodes = [n for i, n in enumerate(self.nodes) if i != node_idx]
    self.directions = [d for i, d in enumerate(self.directions) if i != node_idx]

    self.open_edges = [e for e in self.open_edges if e.name not in (leg1, leg2, parent)]
    self.internal_edges = [e for e in self.internal_edges if e.name != parent]

    fused_edge = OpenEdge(
      name=fused_name,
      number=min(edge1.number, edge2.number),
      direction=edge1.direction,
      irreps=fused_irreps,
      is_fused=True,
      original_irreps=[edge1.irreps, edge2.irreps],
    )
    self.open_edges.append(fused_edge)

    if not parent_was_internal:
      self.open_edges.append(parent_edge)

      dummy_name = f"__dummy_vacuum_{fused_name}_{parent}__"
      max_num = max((e.number for e in self.open_edges + getattr(self, "internal_edges", [])), default=0)

      dummy_edge = OpenEdge(
        name=dummy_name,
        number=max_num + 1,
        direction=1,
        irreps=[(0, 1)],  # what happens with dim 0?
        is_fused=False,
      )
      self.open_edges.append(dummy_edge)

      if direction == NodeType.fusion:
        new_node = (fused_name, dummy_name, parent)
      else:  # splitting
        new_node = (parent, fused_name, dummy_name)

      self.nodes.append(new_node)
      self.directions.append(direction)

    if parent_was_internal and fused_name != parent:
      self.nodes = [tuple(fused_name if e == parent else e for e in n) for n in self.nodes]

    return fused_edge, parent, parent_was_internal

  def determine_internal_charge_sectors(self):
    forward_sets: dict[Any, set[Any]] = {}

    for edge in self.open_edges:
      sectors = [irrep[0] for irrep in edge.irreps]
      if not sectors:
        raise ValueError(f"No charge at edge {edge}")
      forward_sets[edge.name] = set(sectors)

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

  # TODO: redo legs as though the contraction is impicity
  def contract_trees(self, other: "FusionTree", legs_self: list[int], legs_other: list[int]) -> "FusionTree":
    if len(legs_self) != len(self.open_edges) or len(legs_other) != len(other.open_edges):
      raise ValueError("legs_self/legs_other must have one entry per open edge")

    self_name_of = {legs_self[i]: self.open_edges[i].name for i in range(len(legs_self))}
    other_name_of = {legs_other[i]: other.open_edges[i].name for i in range(len(legs_other))}
    contracted_labels = sorted(l for l in legs_self if l > 0)
    leg_pairs = [(self_name_of[l], other_name_of[l]) for l in contracted_labels]

    def relabel(node, replacements):
      return tuple(replacements.get(x, x) for x in node)

    # globally unique consecutive labels for existing internal edges
    k = len(self.internal_edges)
    kp = len(other.internal_edges)
    self_internal_new = {e.name: i + 1 for i, e in enumerate(self.internal_edges)}
    other_internal_new = {e.name: k + i + 1 for i, e in enumerate(other.internal_edges)}
    nodes1 = [relabel(n, self_internal_new) for n in self.nodes]
    nodes2 = [relabel(n, other_internal_new) for n in other.nodes]

    # -- new consecutive labels from k +kp
    next_label = k + kp + 1
    contracted_new_label = {}
    for l in contracted_labels:
      contracted_new_label[l] = next_label
      next_label += 1

    self_contracted_replacements = {self.open_edges[i].name: contracted_new_label[legs_self[i]] for i in range(len(legs_self)) if legs_self[i] > 0}
    other_contracted_replacements = {
      other.open_edges[i].name: contracted_new_label[legs_other[i]] for i in range(len(legs_other)) if legs_other[i] > 0
    }
    nodes1 = [relabel(n, self_contracted_replacements) for n in nodes1]
    nodes2 = [relabel(n, other_contracted_replacements) for n in nodes2]

    match_irreps_on_legs: list[list] = [list(pair) for pair in leg_pairs]

    # relabel negative edges
    self_open_replacements = {self.open_edges[i].name: legs_self[i] for i in range(len(legs_self)) if legs_self[i] < 0}
    other_open_replacements = {other.open_edges[i].name: legs_other[i] for i in range(len(legs_other)) if legs_other[i] < 0}
    nodes1 = [relabel(n, self_open_replacements) for n in nodes1]
    nodes2 = [relabel(n, other_open_replacements) for n in nodes2]

    nodes = nodes1 + nodes2
    directions = list(self.directions) + list(other.directions)

    def other_slot(node, shared: set):
      return next(x for x in node if x not in shared)

    rename_map: dict = {}

    changed = True
    while changed:
      changed = False
      for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
          shared = set(nodes[i]) & set(nodes[j])
          if len(shared) == 2:
            remaining_i = other_slot(nodes[i], shared)
            remaining_j = other_slot(nodes[j], shared)
            match_irreps_on_legs.append([remaining_i, remaining_j])
            keep, drop = (remaining_i, remaining_j) if remaining_i <= remaining_j else (remaining_j, remaining_i)
            nodes = [n for idx, n in enumerate(nodes) if idx not in (i, j)]
            directions = [d for idx, d in enumerate(directions) if idx not in (i, j)]
            if keep != drop:
              nodes = [relabel(n, {drop: keep}) for n in nodes]
              for old, new in list(rename_map.items()):
                if new == drop:
                  rename_map[old] = keep
              rename_map[drop] = keep
            changed = True
            break
        if changed:
          break

    def resolve(label):
      while label in rename_map:
        label = rename_map[label]
      return label

    # TODO : properties or getters.
    self_open_by_name = {e.name: e for e in self.open_edges}
    other_open_by_name = {e.name: e for e in other.open_edges}
    self_internal_by_name = {e.name: e for e in self.internal_edges}
    other_internal_by_name = {e.name: e for e in other.internal_edges}
    self_internal_orig = {v: k_ for k_, v in self_internal_new.items()}
    other_internal_orig = {v: k_ for k_, v in other_internal_new.items()}
    final_open_source = {legs_self[i]: self.open_edges[i] for i in range(len(legs_self)) if legs_self[i] < 0}
    final_open_source.update({legs_other[i]: other.open_edges[i] for i in range(len(legs_other)) if legs_other[i] < 0})

    def get_irreps(x):
      if x in self_internal_orig:
        e = self_internal_by_name.get(self_internal_orig[x])
        return e.irreps if e else None
      if x in other_internal_orig:
        e = other_internal_by_name.get(other_internal_orig[x])
        return e.irreps if e else None
      if x in final_open_source:
        return final_open_source[x].irreps
      if x in self_open_by_name:
        return self_open_by_name[x].irreps
      if x in other_open_by_name:
        return other_open_by_name[x].irreps
      if x in self_internal_by_name:
        return self_internal_by_name[x].irreps
      if x in other_internal_by_name:
        return other_internal_by_name[x].irreps
      return None

    for a, b in match_irreps_on_legs:
      irreps_a, irreps_b = get_irreps(a), get_irreps(b)
      if irreps_a and irreps_b and irreps_a != irreps_b:
        raise ValueError(f"Irreps mismatch on contracted legs {a!r} (self) vs {b!r} (other): {irreps_a} != {irreps_b}")

    resolved_open_source: dict = {}
    for orig_label, edge in final_open_source.items():
      if resolve(orig_label) == orig_label:
        resolved_open_source[orig_label] = edge
    for orig_label, edge in final_open_source.items():
      resolved_open_source.setdefault(resolve(orig_label), edge)

    open_edges = [
      OpenEdge(name=label, number=i + 1, direction=src.direction, irreps=list(src.irreps))
      for i, (label, src) in enumerate(resolved_open_source.items())
    ]
    internal_names = sorted({x for n in nodes for x in n if isinstance(x, int) and x > 0})
    internal_edges = [InternalEdge(name=name, number=i + 1) for i, name in enumerate(internal_names)]

    merged = FusionTree(open_edges, internal_edges, nodes, directions, self.symmetry)

    if len(merged.open_edges) == 0:
      merged.open_edges = [OpenEdge(name="__scalar_dummy__", number=1, direction=1, irreps=[(0, 1)])]
    elif len(merged.open_edges) == 2:
      e1, e2 = merged.open_edges
      if not merged._legs_share_node(e1.name, e2.name):
        merged._wrap_with_dummy(e1.name, e2.name, NodeType.fusion)

    return merged

  # Can we inline this?
  # Some cases:
  # -- [-1,-2, -3] [-1,-2,-3] with dirs fusion, split
  # -- -> [-1,-1,dummy]
  # -- with drs [-1,1,1] and [-1,-1,1]  i.e. split, fuse
  # -- [-1,-2,int] [int, -3,-4]  stays same
  # ---
  # -- [-1,-2,int_1] [int_1, int_2, -5] [int_2, -3, -4] and [-2,-3,int_1] [-1,int_1, int_2] [int_2, -4, -5]
  # -- f --> [-1,-2,int_1] [int_1, -3, int_2] [int_2, -4, -5]
  # def merge_trees(tree_A, tree_B, legs_A, legs_B):
  #  for legA in legs_A:


if __name__ == "__main__":
  sym = symmnet.symmetry.SU2()

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

  print(tree.determine_internal_charge_sectors())
  print(tree.nodes)
  tree.rmove(0)
  print(tree.determine_internal_charge_sectors())
  print(tree.nodes)  # This is not yet swapped

  print(tree)

  e1 = OpenEdge(name=-1, number=1, direction=1, irreps=[(0, 1), (1, 2), (2, 3)])
  e2 = OpenEdge(name=-2, number=2, direction=-1, irreps=[(0, 1), (1, 4)])
  e3 = OpenEdge(name=-3, number=3, direction=-1, irreps=[(0, 1), (1, 6)])

  tree = FusionTree(open_edges=[e1, e2, e3], internal_edges=[], nodes=[(-1, -2, -3)], directions=[NodeType.splitting], symmetry=SU2())

  print(tree)
  tree.fuse_legs(-2, -3, "fuse")
  print(tree)
  print("nodes: ", tree.nodes)

  print(tree.determine_internal_charge_sectors())  # TODO bug here.

  outer_charges = {-1: [1 / 2], -2: [1 / 2], -3: [1 / 2]}

  outer_edges = make_open_with_charges(outer_charges)

  tree_1 = FusionTree(open_edges=outer_edges, internal_edges=[], nodes=[(-1, -2, -3)], directions=[NodeType.fusion], symmetry=sym)

  outer_charges = {-4: [1 / 2], -5: [1 / 2], -6: [1 / 2]}

  outer_edges = make_open_with_charges(outer_charges)
  tree_2 = FusionTree(open_edges=outer_edges, internal_edges=[], nodes=[(-4, -5, -6)], directions=[NodeType.splitting], symmetry=sym)
  print(f"Tree 1: {tree_1}")
  print(f"Tree_2: {tree_2}")
  # contracted = tree_2.contract_trees(tree_1, [-4, -6], [-1, -2])
  # p#rint("after contract")
  # print(contracted)

  sym = SU2()

  def mk_open(names):
    return [OpenEdge(name=n, number=i + 1, direction=1, irreps=[(0, 1), (1, 2)]) for i, n in enumerate(names)]

  oe1 = mk_open([-1, -2, -3, -4, -5])
  tree1 = FusionTree(
    oe1,
    [InternalEdge("i1", 1), InternalEdge("i2", 2)],
    [(-1, -2, "i1"), ("i1", "i2", -5), ("i2", -3, -4)],
    [NodeType.splitting, NodeType.splitting, NodeType.splitting],
    sym,
  )

  oe2 = mk_open([-1, -2, -3, -4])
  tree2 = FusionTree(oe2, [InternalEdge("j1", 1)], [(-1, -2, "j1"), ("j1", -3, -4)], [NodeType.fusion, NodeType.splitting], sym)

  legs_self = [-3, -4, 1, 2, -2]
  legs_other = [1, 2, -1, -5]

  merged = tree1.contract_trees(tree2, legs_self, legs_other)
  print("open edges:", sorted([e.name for e in merged.open_edges], key=str))
  print("internal edges:", sorted([e.name for e in merged.internal_edges], key=str))
  print("nodes = ", merged.nodes)
  print("directions:", merged.directions)
