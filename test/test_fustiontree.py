import pytest
from symmnet.fusiontree import FusionTree, NodeType, TreeSort
from symmnet.symmetry import SU2


@pytest.fixture
def fresh_tree_5():
  sym = SU2()
  return FusionTree(
    open_edges=[-1, -2, -3, -4, -5],
    internal_edges=["i1", "i2"],
    nodes=[(-1, -2, "i1"), ("i1", -3, "i2"), ("i2", -4, -5)],
    directions=(NodeType.fusion, NodeType.fusion, NodeType.fusion),
    symmetry=sym,
  )

@pytest.fixture
def left_aligned_tree():
  return FusionTree(
    open_edges=[-1,-2,-3,-4,-5],
    internal_edges=['i1','i2'],
    nodes=[(-1,-2,'i'),('i',-3,-4)],
    directions=[NodeType.fusion, NodeType.fusion]
  )

@pytest.fixture
def right_aligned_tree():
  return FusionTree(
    open_edges=[-1,-2,-3,-4,-5],
    internal_edges=['i1','i2'],
    nodes=[(-1,'i', -4),(-2,-3,'i')],
    directions=[NodeType.fusion, NodeType.fusion]
  )

def test_basic_move_left(left_aligned_tree):
  t1 = left_aligned_tree
  t1.fmove('i')
  print("Left: ", t1.nodes)
  assert t1.nodes == [(-1, 'i', -4), (-2,-3,'i')]

def test_basic_move_right(right_aligned_tree):
  t1 = right_aligned_tree
  t1.fmove("i")
  assert t1.nodes == [(-1,-2,'i'),('i',-3,-4)]
  


def test_paper_equation_4_11_transformation():
  sym = SU2()

  open_legs = [-1, -2, -3, -4, -5, -6, -7, -8]

  tau_i = FusionTree(
    open_edges=open_legs,
    internal_edges=[1, 2, 3, 4, 5],
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
    open_edges=open_legs,
    internal_edges=[1, 2, 3, 4, 5],
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
  open_edges = [-a for a in range(1,7)]

  figure_50_tree = FusionTree(
    open_edges=open_edges,
    internal_edges=[1,2,3],
    nodes=[(-1,-2,1),(1,-4,2),(2,-3,3),(3,-5,-6)],
    directions=[NodeType.fusion, NodeType.splitting, NodeType.fusion, NodeType.splitting]
  )
  assert figure_50_tree.determine_type() == TreeSort.yoga
  figure_50_tree.fmove(2)
  assert figure_50_tree.determine_type() == TreeSort.simple

@pytest.fixture
def minimal_monster_tree():
  return FusionTree(
    open_edges=[-1,-2,-3,-4],
    internal_edges=['i'],
    nodes=[(-1,'i',-2),('i',-3,-4)],
    directions=[NodeType.splitting, NodeType.fusion]
  )

@pytest.fixture
def minimal_monster_tree_right():
  return FusionTree(
    open_edges=[-1,-2,-3,-4],
    internal_edges=['i'],
    nodes=[(-1,-2,'i'),(-3, 'i',-4)],
    directions=[NodeType.splitting, NodeType.fusion]
  )

def test_is_monster(minimal_monster_tree, minimal_monster_tree_right):
  tree = minimal_monster_tree
  assert tree.determine_type() == TreeSort.monster
  tree2 = minimal_monster_tree_right
  assert tree2.determine_type() == TreeSort.monster


# def test_pentagon():
#   left_tree = FusionTree(
#     open_edges=[-1, -2, -3, -4, -5],
#     internal_edges=["i1", "i2"],
#     nodes=[(-1, -2, "i1"), ("i1", -3, "i2"), ("i2", -4, -5)],
#     directions=(NodeType.fusion, NodeType.fusion, NodeType.fusion),
#   )
# 
#   left_tree.fmove("i1")
#   left_tree.fmove('i2')
#   left_tree.fmove("i1")
# 
#   right_tree = FusionTree(
#     open_edges=[-1, -2, -3, -4, -5],
#     internal_edges=["i1", "i2"],
#     nodes=[(-1, -2, "i1"), ("i1", -3, "i2"), ("i2", -4, -5)],
#     directions=(NodeType.fusion, NodeType.fusion, NodeType.fusion),
#   )
#   right_tree.fmove(edge='i2')
#   right_tree.fmove('i1')
# 
#   print("This one will fail because we are not checking for relabeling")
#   # TODO: implement a function same_up_to_relabeling.
#   assert left_tree.nodes == right_tree.nodes