from functools import lru_cache
import numpy as np
from sympy.physics.wigner import clebsch_gordan

def F_matrix(a,b,c,d,e,f):
  pass

def possible_charge_sectors(a:float, b:float) -> list[float]:
  return list(np.arange(abs(a - b), a + b + 1, 1.0))

def possible_charge_sectors_int(a:int, b:int) -> list[int]:
  return list(np.arange(abs(a-b),(a+b)+1, 2))

print(possible_charge_sectors_int(2,1))