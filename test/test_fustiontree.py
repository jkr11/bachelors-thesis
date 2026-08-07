import pytest
from symmnet.fusiontree import FusionTree, NodeType, TreeSort, OpenEdge, InternalEdge
from symmnet.symmetry import SU2
import symmnet.symmetry as symmetry


def make_open(edges: list) -> list[OpenEdge]:
  return [OpenEdge(name=e, number=i + 1, direction=-1) for i, e in enumerate(edges)]


def make_internal(edges: list) -> list[InternalEdge]:
  return [InternalEdge(name=e, number=i + 1) for i, e in enumerate(edges)]


def make_open_with_charges(edge_charges: dict) -> list[OpenEdge]:
  return [OpenEdge(name=e, number=i + 1, direction=-1, irreps=[(q, 1) for q in charges]) for i, (e, charges) in enumerate(edge_charges.items())]


# -----------------------------------------------------------


@pytest.fixture
def fresh_tree_5():
  sym = SU2()
  return FusionTree(
    open_edges=make_open([-1, -2, -3, -4, -5]),
    internal_edges=make_internal(["i1", "i2"]),
    nodes=[(-1, -2, "i1"), ("i1", -3, "i2"), ("i2", -4, -5)],
    directions=[NodeType.fusion, NodeType.fusion, NodeType.fusion],
    symmetry=sym,
  )


@pytest.fixture
def left_aligned_tree():
  return FusionTree(
    open_edges=make_open([-1, -2, -3, -4]),
    internal_edges=make_internal(["i"]),
    nodes=[(-1, -2, "i"), ("i", -3, -4)],
    directions=[NodeType.fusion, NodeType.fusion],
  )


@pytest.fixture
def right_aligned_tree():
  return FusionTree(
    open_edges=make_open([-1, -2, -3, -4]),
    internal_edges=make_internal(["i"]),
    nodes=[(-1, "i", -4), (-2, -3, "i")],
    directions=[NodeType.fusion, NodeType.fusion],
  )


def test_basic_move_left(left_aligned_tree):
  t1 = left_aligned_tree
  t1.fmove("i")
  print("Left: ", t1.nodes)
  assert t1.nodes == [(-1, "i", -4), (-2, -3, "i")]


def test_basic_move_right(right_aligned_tree):
  t1 = right_aligned_tree
  t1.fmove("i")
  assert t1.nodes == [(-1, -2, "i"), ("i", -3, -4)]


def test_paper_equation_4_11_transformation():
  sym = SU2()

  open_legs = [-1, -2, -3, -4, -5, -6, -7, -8]

  tau_i = FusionTree(
    open_edges=make_open(open_legs),
    internal_edges=make_internal([1, 2, 3, 4, 5]),
    nodes=[
      (-2, -3, 1),
      (1, -4, 2),
      (-1, 2, 3),
      (3, 4, 5),
      (4, -5, -6),
      (5, -7, -8),
    ],
    directions=[NodeType.fusion] * 3 + [NodeType.splitting] * 3,
    symmetry=sym,
  )

  tau_f = FusionTree(
    open_edges=make_open(open_legs),
    internal_edges=make_internal([1, 2, 3, 4, 5]),
    nodes=[
      (-2, -3, 1),
      (1, -4, 2),
      (-1, 2, 3),
      (3, -5, 4),
      (4, 5, -8),
      (5, -6, -7),
    ],
    directions=[NodeType.fusion] * 3 + [NodeType.splitting] * 3,
    symmetry=sym,
  )

  tau_i.fmove(4)
  tau_i.fmove(5)
  assert tau_i.nodes == tau_f.nodes


def test_yoga_fmove():
  open_edges = [-a for a in range(1, 7)]

  figure_50_tree = FusionTree(
    open_edges=make_open(open_edges),
    internal_edges=make_internal([1, 2, 3]),
    nodes=[(-1, -2, 1), (1, -4, 2), (2, -3, 3), (3, -5, -6)],
    directions=[NodeType.fusion, NodeType.splitting, NodeType.fusion, NodeType.splitting],
  )
  assert figure_50_tree.determine_type() == TreeSort.yoga
  figure_50_tree.fmove(2)
  assert figure_50_tree.determine_type() == TreeSort.simple


@pytest.fixture
def minimal_monster_tree():
  return FusionTree(
    open_edges=make_open([-1, -2, -3, -4]),
    internal_edges=make_internal(["i"]),
    nodes=[(-1, "i", -2), ("i", -3, -4)],
    directions=[NodeType.splitting, NodeType.fusion],
  )


@pytest.fixture
def minimal_monster_tree_right():
  return FusionTree(
    open_edges=make_open([-1, -2, -3, -4]),
    internal_edges=make_internal(["i"]),
    nodes=[(-1, -2, "i"), (-3, "i", -4)],
    directions=[NodeType.splitting, NodeType.fusion],
  )


def test_is_monster(minimal_monster_tree, minimal_monster_tree_right):
  tree = minimal_monster_tree
  assert tree.determine_type() == TreeSort.monster
  tree2 = minimal_monster_tree_right
  assert tree2.determine_type() == TreeSort.monster


def test_charge_sectors_fib():
  sym = symmetry.Fib()
  outer = {
    -1: [1],
    -2: [1],
    -3: [1],
  }

  tree = FusionTree(
    open_edges=make_open_with_charges(outer),
    internal_edges=make_internal(["internal_1"]),
    nodes=[(-1, -2, "internal_1"), ("internal_1", -3, "internal_2")],
    directions=[NodeType.fusion, NodeType.fusion],
    symmetry=sym,
  )

  valid_states = tree.determine_internal_charge_sectors()

  formatted_sectors = []
  for state in valid_states:
    vector = [state["internal_1"], state["internal_2"], state[-1], state[-2], state[-3]]
    formatted_sectors.append(vector)

  truth = [[0, 1, 1, 1, 1], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1]]

  formatted_sectors.sort()

  assert formatted_sectors == truth


def test_charge_sectors_su2():
  sym = symmetry.SU2()

  paper_outer_boundary = {
    -1: [0, 1],  # j1
    -2: [0, 1],  # j2
    -3: [0, 1],  # j3
    -4: [0, 1],  # j4
  }

  paper_tree = FusionTree(
    open_edges=make_open_with_charges(paper_outer_boundary),
    internal_edges=make_internal(["internal_1"]),
    nodes=[(-1, -2, "internal_1"), ("internal_1", -3, -4)],
    directions=[NodeType.fusion, NodeType.fusion],
    symmetry=sym,
  )

  valid_paper_states = paper_tree.determine_internal_charge_sectors()

  # Formatting to match 4.6
  formatted_sectors = []
  for state in valid_paper_states:
    vector = [state["internal_1"], state[-1], state[-2], state[-3], state[-4]]
    formatted_sectors.append(vector)

  # After 4.6 in programming guide
  example_truth = [
    [0.0, 0, 0, 0, 0],
    [0.0, 0, 0, 1, 1],
    [0.0, 1, 1, 0, 0],
    [0.0, 1, 1, 1, 1],
    [1.0, 0, 1, 0, 1],
    [1.0, 0, 1, 1, 0],
    [1.0, 0, 1, 1, 1],
    [1.0, 1, 0, 0, 1],
    [1.0, 1, 0, 1, 0],
    [1.0, 1, 0, 1, 1],
    [1.0, 1, 1, 0, 1],
    [1.0, 1, 1, 1, 0],
    [1.0, 1, 1, 1, 1],
    [2.0, 1, 1, 1, 1],
  ]

  formatted_sectors.sort()

  assert formatted_sectors == example_truth


# def test_pentagon():
#   left_tree = FusionTree(
#     list_of_open_edges=make_open([-1, -2, -3, -4, -5]),
#     list_of_internal_edges=make_internal(["i1", "i2"]),
#     fusion_tree=[(-1, -2, "i1"), ("i1", -3, "i2"), ("i2", -4, -5)],
#     fusion_tree_directions=(NodeType.fusion, NodeType.fusion, NodeType.fusion),
#   )
#
#   left_tree.fmove("i1")
#   left_tree.fmove('i2')
#   left_tree.fmove("i1")
#
#   right_tree = FusionTree(
#     list_of_open_edges=make_open([-1, -2, -3, -4, -5]),
#     list_of_internal_edges=make_internal(["i1", "i2"]),
#     fusion_tree=[(-1, -2, "i1"), ("i1", -3, "i2"), ("i2", -4, -5)],
#     fusion_tree_directions=(NodeType.fusion, NodeType.fusion, NodeType.fusion),
#   )
#   right_tree.fmove(edge='i2')
#   right_tree.fmove('i1')
#
#   print("This one will fail because we are not checking for relabeling")
#   # TODO: implement a function same_up_to_relabeling.
#   assert left_tree.fusionTree == right_tree.fusionTree
