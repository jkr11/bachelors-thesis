import numpy as np
from sympy.physics.quantum.cg import clebsch_gordan
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
                  c_fuse[i, j, k] = clebsch_gordan(j1, j2, j3, m1, m2, m3)
      return c_fuse    
      
  @classmethod
  @lru_cache
  def get_splitting_tensor(cls, j1, j2, j3):
      return cls.get_fusion_tensor(j1, j2, j3).transpose(2,0,1)


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

print(get_block_sparse_fusion([0.5,1],[0.5,1]))

