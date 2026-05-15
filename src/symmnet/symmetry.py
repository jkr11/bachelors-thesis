from functools import lru_cache
import numpy as np
from sympy.physics.wigner import clebsch_gordan
from abc import ABC, abstractmethod

type sector = int|float

class Symmetry(ABC):
  @classmethod
  @abstractmethod
  def possible_charge_sectors(cls, a:sector,b:sector) -> list[sector]:
    pass

  @staticmethod
  @classmethod
  @abstractmethod
  def structural_tensor(cls, a,b,c,ma,mb,mc):
    pass

  #@staticmethod
  #@classmethod
  #@abstractmethod
  #def R_symbol(cls, a,b,c):
  #  pass

  @classmethod
  def is_valid(cls, a,b,c):
    return c in cls.possible_charge_sectors(a,b)

class Z2(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a:sector, b:sector) -> list[sector]:
    return [(a + b) % 2]

class U1(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a:float, b:float) -> list[float]:
    return [a + b]

  @staticmethod
  @classmethod
  def structural_tensor(cls, a, b, c, ma, mb, mc):
    return 1.0 if a + b == c else 0.0

class SU2(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a:float, b:float) -> list[float]:
    return list(np.arange(abs(a - b), a + b + 1, 1.0))

  @classmethod
  @lru_cache(maxsize=1024)
  def structural_tensor(cls, a, b,c,ma,mb,mc):
    return clebsch_gordan(a,b,c, ma,mb,mc)

  #@classmethod
  #def R_symbol(cls, a,b,c):
  #  return (-1)^(a + b - c)

class SU2k(Symmetry):
  def __init__(self, k: int):
    self.k = k

  def possible_charge_sectors(self, a:float, b:float) -> list[float]:
    return list(np.arange(abs(a-b), self.k - (a + b) + 1, 1.0))

# TODO: either remove this or make this take arbitrariliy many sims.
class ProductSymmetry(Symmetry):
  def __init__(self, sym1 : Symmetry, sym2:Symmetry):
    self.sym1 = sym1
    self.sym2 = sym2

  def possible_charge_sectors(self, a, b):
    outcomes1 = self.sym1.possible_charge_sectors(a[0], b[0])
    outcomes2 = self.sym2.possible_charge_sectors(a[1], b[1])
    return [(j, q) for j in outcomes1 for q in outcomes2]

  @classmethod
  @staticmethod
  def structural_tensor(cls, a,b,c,ma,mb,mc):
    pass

print(SU2.possible_charge_sectors(1.5,0.5))

electroweak_sym = ProductSymmetry(SU2(), U1())


particle_a = (0.5, -1)
particle_b = (0.5, 1)

allowed = electroweak_sym.possible_charge_sectors(particle_a, particle_b)

print(allowed)