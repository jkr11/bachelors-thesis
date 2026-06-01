import numpy as np
from sympy.physics.quantum.cg import CG
from functools import lru_cache

# So how do CFuse and CSplit work? If we have two (irreps) V_(j1) and V_(j2), CFuse acts as Cfuse : V_(j1) \otimes V_(j2) \to V_(j12)
# Its elements are therefore (C_fuse)_(m12)^(m1,m2) = (<j1,m1| <j2,m2|)|j12,m12>


# TODO: make this a lookup table.
class ClebschGordan:
  @classmethod
  @lru_cache
  def get_fusion_tensor(cls, j1, j2, j3):
    d1 = int(2 * j1 + 1)
    d2 = int(2 * j2 + 1)
    d3 = int(2 * j3 + 1)
    c_fuse = np.zeros((d1, d2, d3))
    M1 = np.arange(-j1, j1 + 1)
    M2 = np.arange(-j2, j2 + 1)
    M3 = np.arange(-j3, j3 + 1)
    for i, m1 in enumerate(M1):
      for j, m2 in enumerate(M2):
        for k, m3 in enumerate(M3):
          c_fuse[i, j, k] = float(CG(j1, j2, j3, m1, m2, m3).doit())

    return c_fuse

  @classmethod
  @lru_cache
  def get_splitting_tensor(cls, j1, j2, j3):
    return cls.get_fusion_tensor(j1, j2, j3).transpose(2, 0, 1)


j1, j2, j3 = 0.5, 0.5, 1

c_fuse = ClebschGordan.get_fusion_tensor(j1, j2, j3)
c_split = ClebschGordan.get_splitting_tensor(j1, j2, j3)

identity_check = np.tensordot(c_fuse, c_split, axes=([0, 1], [1, 2]))
print(identity_check)


def get_block_sparse_fusion(leg1_sectors, leg2_sectors):
  blocks = {}

  for j1 in leg1_sectors:
    for j2 in leg2_sectors:
      j3_min = abs(j1 - j2)
      j3_max = j1 + j2

      for j3 in np.arange(j3_min, j3_max + 1, 1):
        block = ClebschGordan.get_fusion_tensor(j1, j2, j3)

        blocks[(j1, j2, j3)] = block

  return blocks


print(get_block_sparse_fusion([0.5, 1], [0.5, 1]))


def build_structural_tensor(fusion_tree, irreps, external_order):
  unique_edges = set()
  for node in fusion_tree:
    _, l1, l2, l3 = node
    unique_edges.update([l1, l2, l3])

  edge_to_char = {edge: chr(97 + i) for i, edge in enumerate(unique_edges)}

  einsum_inputs = []
  tensors = []

  for node_type, l1, l2, l3 in fusion_tree:
    j1, j2, j3 = irreps[l1], irreps[l2], irreps[l3]

    if node_type == "fuse":
      tensor = ClebschGordan.get_fusion_tensor(j1, j2, j3)
    elif node_type == "split":
      tensor = ClebschGordan.get_splitting_tensor(j1, j2, j3)
    else:
      raise ValueError(f"Unknown node type: {node_type}")

    tensors.append(tensor)

    indices = "".join([edge_to_char[l] for l in (l1, l2, l3)])
    einsum_inputs.append(indices)

  einsum_output = "".join([edge_to_char[l] for l in external_order])

  einsum_string = ",".join(einsum_inputs) + "->" + einsum_output

  print(f"Executing einsum: {einsum_string}")

  return np.einsum(einsum_string, *tensors)


tree = [("fuse", -1, -2, 1), ("fuse", 1, -3, -4)]

irrep_assignments = {-1: 1, -2: 1, -3: 1, -4: 1, 1: 2}

external_legs = [-1, -2, -3, -4]

structural_tensor = build_structural_tensor(tree, irrep_assignments, external_legs)

print(f"Resulting tensor shape: {structural_tensor.shape}")
