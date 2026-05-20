from functools import lru_cache
import numpy as np
from sympy.physics.wigner import clebsch_gordan
from abc import ABC, abstractmethod
from collections.abc import Sequence

type sector = int | float


class Symm[T](ABC):
  @abstractmethod
  def possible_charge_sectors(self, a: T, b: T) -> Sequence[T]:
    pass

  @abstractmethod
  def R_symbol(self, a: T, b: T, c: T) -> float:
    pass

  @abstractmethod
  def F_symbol(self, a: T, b: T, c: T) -> float:
    pass


class sZ2(Symm):
  def possible_charge_sectors(self, a: int, b: int) -> list[int]:
    return [(a + b) % 2]


class sU1(Symm):
  def possible_charge_sectors(self, a: float, b: float) -> list[float]:
    return [a + b]


class sSU2(Symm):
  def possible_charge_sectors(self, a: float, b: float) -> list[float]:
    return list(np.arange(abs(a - b), a + b + 1, step=1.0))


class ProductSymm(Symm):
  def __init__(self, *symmetries):
    self.symmetries = symmetries

  def possible_charge_sectors(self, a, b) -> list[tuple]:
    assert len(a) == len(b)
    outcomes = {}
    return []


class Symmetry(ABC):
  @classmethod
  @abstractmethod
  def possible_charge_sectors(cls, a: sector, b: sector) -> Sequence[sector]:
    pass

  # @staticmethod
  # @classmethod
  # @abstractmethod
  # def structural_tensor(cls, a,b,c,ma,mb,mc):
  #  pass

  # @staticmethod
  # @classmethod
  # @abstractmethod
  # def R_symbol(cls, a,b,c):
  #  pass

  # @abstractmethod
  # @classmethod
  # def F_symbol(cls, a,b,c,abc,d,e):
  #  pass

  @classmethod
  def is_valid(self, a, b, c):
    return c in self.possible_charge_sectors(a, b)


class Z2(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a: float, b: float) -> list[float]:
    return [(a + b) % 2]


class U1(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a: float, b: float) -> list[float]:
    return [a + b]

  @staticmethod
  @classmethod
  def structural_tensor(cls, a, b, c, ma, mb, mc):
    return 1.0 if a + b == c else 0.0


class SU2(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a: float, b: float) -> list[float]:
    return list(np.arange(abs(a - b), a + b + 0.1, 1.0))

  @classmethod
  @lru_cache(maxsize=1024)
  def structural_tensor(cls, a, b, c, ma, mb, mc):
    return clebsch_gordan(a, b, c, ma, mb, mc)

  # @classmethod
  # def R_symbol(cls, a,b,c):
  #  return (-1)^(a + b - c)


class SU2_3(Symmetry):
  @classmethod
  def possible_charge_sectors(self, a: float, b: float) -> list[float]:
    return list(np.arange(abs(a - b), min(a + b, 3.0 - a + b) + 0.1, 1.0))


class Fib(Symmetry):
  @classmethod
  def possible_charge_sectors(cls, a: float, b: float) -> list[float]:
    if a == 0.0:
      return [b]
    if b == 0.0:
      return [a]
    if a == 1.0 and b == 1.0:
      return [0.0, 1.0]
    return []


type Sector = list[sector]


# TODO: either remove this or make this take arbitrariliy many sims.
class ProductSymmetry(Symmetry):
  def __init__(self, sym1: Symmetry, sym2: Symmetry):
    self.sym1 = sym1
    self.sym2 = sym2

  def possible_charge_sectors(self, a, b):
    outcomes1 = self.sym1.possible_charge_sectors(a[0], b[0])
    outcomes2 = self.sym2.possible_charge_sectors(a[1], b[1])
    return [(j, q) for j in outcomes1 for q in outcomes2]

  @classmethod
  @staticmethod
  def structural_tensor(cls, a, b, c, ma, mb, mc):
    pass

  # def R_symbol(self, a,b,c):
  #  return self.sym1.R_symbol(a[0],b[0],c[0]) * self.sym2.R_symbol(a[1],b[1],c[1])


print(SU2.possible_charge_sectors(1.5, 0.5))

electroweak_sym = ProductSymmetry(SU2(), U1())


particle_a = (0.5, -1)
particle_b = (0.5, 1)

allowed = electroweak_sym.possible_charge_sectors(particle_a, particle_b)

print(allowed)
