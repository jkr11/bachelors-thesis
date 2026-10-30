import numpy as np


def _bit(x, N):
  return [int(b) for b in format(x, f"0{N}b")]


def num(b):
  return int("".join(map(str, b)), 2)


def flip(b, i, j):
  b = b.copy()
  b[i] ^= 1
  b[j] ^= 1
  return b


# Cite the book it got this from, some kinda monograph on quantum simulation? or
# was it a lecture note?
def build_xxz_hamiltonian(N, J, Delta, periodic=False):
  dim = 2**N
  H = np.zeros((dim, dim), dtype=float)
  bonds = N if periodic else N - 1

  for x in range(dim):
    b = _bit(x, N)
    for i in range(bonds):
      j = (i + 1) % N
      if b[i] == b[j]:
        H[x, x] -= J * Delta / 4
      else:
        H[x, x] += J * Delta / 4
        y = num(flip(b, i, j))
        H[x, y] -= J / 2
  return H


def construct_spin_operators(N):
  dim = 2**N

  s_x = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
  s_y = 0.5 * np.array([[0, -1j], [1j, 0]], dtype=complex)
  s_z = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
  identity = np.eye(2, dtype=complex)

  def get_op(op, site) -> np.ndarray:
    res = np.array([[1]], dtype=complex)
    for j in range(N):
      current_mat = op if j == site else identity
      res = np.kron(res, current_mat)
    return res

  Sx = sum(get_op(s_x, i) for i in range(N))
  Sy = sum(get_op(s_y, i) for i in range(N))
  Sz = sum(get_op(s_z, i) for i in range(N))

  Sp = Sx + 1j * Sy
  Sm = Sx - 1j * Sy

  S2 = Sx @ Sx + Sy @ Sy + Sz @ Sz

  return np.real(S2), np.real(Sz), np.real(Sm), np.real(Sx), Sy, np.real(Sp)
  # Only Sy is not real