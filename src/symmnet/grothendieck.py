"""
Implements the actual grothendieck-ring underlying the fusion algebra (or is it the same ?). This allows us to pass in the entire dicts. 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import numpy as np

# Charge = TypeVar("Charge", bound=Hashable) # TODO move to this for subclassing if wanted
Charge = Any


@dataclass(frozen=True)
class Rep:
  "This is a ring element. .e. 2 * 1/2 + 3/2 is represented as"

  "{1/2 : 2, 3/2 : 1}"
  symmetry: Symmetry
  terms: dict[Charge, int]

  def __post_init__(self):
    terms = {charge: multiplicity for charge, multiplicity in self.terms.items() if multiplicity != 0}

    object.__setattr__(self, "terms", terms)

  def __add__(self, other: Rep) -> Rep:
    result = dict(self.terms)
    for charge, multiplicity in other.terms.items():
      result[charge] = result.get(charge, 0) + multiplicity
      if result[charge] == 0:
        del result[charge]
    return Rep(self.symmetry, result)

  def __sub__(self, other: Rep) -> Rep:
    raise NotImplementedError("Is sub necessary to implement?")

  def __mul__(self, other: Rep | int) -> Rep:
    """
    lifts out the symmry fusion operator.
    """
    if isinstance(other, int):
      return Rep(
        self.symmetry,
        {charge: mult * other for charge, mult in self.terms.items()},
      )
    combined_terms: dict[Charge, int] = {}
    for charge_a, mult_a in self.terms.items():
      for charge_b, mult_b in other.terms.items():
        fusion_result = self.symmetry.fusion(charge_a, charge_b)
        for charge_c, N_abc in fusion_result.items():
          combined_terms[charge_c] = combined_terms.get(charge_c, 0) + mult_a * mult_b * N_abc

    return Rep(self.symmetry, combined_terms)

  def __rmul__(self, other: int) -> Rep:
    return self.__mul__(other)

  def __repr__(self) -> str:
    """
    E.g., "2·[0] + [1]"
    """
    if not self.terms:
      return "0"

    parts = []
    for charge, mult in self.terms.items():
      if mult == 1:
        parts.append(f"[{charge}]")
      elif mult == -1:
        parts.append(f"-[{charge}]")
      elif mult < 0:
        parts.append(f"- {abs(mult)}·[{charge}]")
      else:
        parts.append(f"{mult}·[{charge}]")

    res = parts[0]
    for part in parts[1:]:
      if part.startswith("-"):
        res += f" - {part[1:].lstrip()}"
      else:
        res += f" + {part}"
    return res


class Symmetry(ABC):
  def irrep(self, charge: Charge) -> Rep:
    return Rep(self, {charge: 1})

  @property
  @abstractmethod
  def unit(self) -> Charge:
    raise NotImplementedError

  @property
  def zero(self) -> Rep:
    return Rep(self, {})

  @property
  def one(self) -> Rep:
    return self.irrep(self.unit)

  @abstractmethod
  def fusion(self, a: Charge, b: Charge) -> dict[Charge, int]:
    """
    This is the actual rule [a] * [b] = sum_c N^C_ab [c].
    """
    raise NotImplementedError

  def possible_charge_sectors(
    self,
    a: Charge,
    b: Charge,
  ) -> tuple[Charge, ...]:
    return tuple(self.fusion(a, b).keys())

  def is_valid(
    self,
    a: Charge,
    b: Charge,
    c: Charge,
  ) -> bool:
    return self.fusion(a, b).get(c, 0) != 0

  @abstractmethod
  def dual(self, a: Charge) -> Charge:
    """
    Charge of the dual representation (antiparticle)
    """
    raise NotImplementedError

  # These do not have multiplicities yet. Fix.
  @abstractmethod
  def R_symbol(
    self,
    a: Charge,
    b: Charge,
    c: Charge,
  ) -> Any:
    raise NotImplementedError

  @abstractmethod
  def F_symbol(
    self,
    a: Charge,
    b: Charge,
    c: Charge,
    d: Charge,
    e: Charge,
    f: Charge,
  ) -> Any:
    raise NotImplementedError


class Z2(Symmetry):
  @property
  def unit(self) -> int:
    return 0

  def fusion(self, a: int, b: int) -> dict[int, int]:
    return {
      (a + b) % 2: 1,
    }

  def dual(self, a: int) -> int:
    return a

  def R_symbol(self, a: int, b: int, c: int) -> int:
    return 1

  def F_symbol(self, a, b, c, d, e, f) -> int:
    return 1

class sVect(Z2):
  def twist(self, a):
    return (-1)**a

class SU2(Symmetry):
  @property
  def unit(self) -> float:
    return 0.0

  def fusion(self, a: float, b: float) -> dict[float, int]:
    min_dim = abs(a - b)
    max_dim = a + b

    return {d: 1 for d in np.arange(min_dim, max_dim + 0.1, 1.0)}

  def dual(self, a: float) -> float:
    return a

  def R_symbol(self, a: float, b: float, c: float) -> Any:
    raise NotImplementedError("R_symbol")

  def F_symbol(self, a: float, b: float, c: float, d: float, e: float, f: float) -> Any:
    raise NotImplementedError("F_symbol")


if __name__ == "__main__":
  su2 = SU2()

  j0 = su2.irrep(0)
  j1_2 = su2.irrep(1 / 2)
  j1 = su2.irrep(2 / 2)

  print("Irreps:")
  print("Spin 0  :", j0)
  print("Spin 1/2:", j1_2)
  print("Spin 1  :", j1)

  print("1/2 ⊗ 1/2 =", j1_2 * j1_2)

  print("1/2 ⊗ 1   =", j1_2 * j1)

  print("1 ⊗ 1     =", j1 * j1)

  cube = j1_2 * j1_2 * j1_2
  print("(1/2)^(⊗3) =", cube)
