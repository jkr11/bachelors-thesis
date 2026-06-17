import numpy as np
from symmnet.symmetry import Fib


def test_fib_pentagon():
  s = Fib()

  sectors = [0.0, 1.0]  # 1 = tau

  phi = (1 + np.sqrt(5)) / 2

  def ok(a, b, c, d):
    """
    Check pentagon identity for Fib on a fixed quadruple.
    Since Fib is tiny, we brute force everything.
    """

    for e in s.possible_charge_sectors(a, b):
      for f in s.possible_charge_sectors(b, c):
        for g in s.possible_charge_sectors(e, c):
          for i in s.possible_charge_sectors(c, d):
            for j in s.possible_charge_sectors(b, i):
              for k in s.possible_charge_sectors(f, d):
                lhs = s.F_symbol(a, b, c, d, e, f) * s.F_symbol(a, e, d, c, g, k)

                rhs = s.F_symbol(b, c, d, e, f, i) * s.F_symbol(a, b, i, d, e, j) * s.F_symbol(a, j, d, b, k, g)

                if not np.isclose(lhs, rhs):
                  return False

    return True

  # Fib is tiny → just test all nontrivial cases
  for a in sectors:
    for b in sectors:
      for c in sectors:
        for d in sectors:
          assert ok(a, b, c, d)

test_fib_pentagon()