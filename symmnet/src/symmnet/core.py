from abc import ABC, abstractmethod, abstractproperty
from typing import List, Tuple, Literal
import numpy as np
from enum import IntEnum
import networkx as nx
import matplotlib.pyplot as plt


class Tensor(ABC):
  """
  Abstract Base Class defining traits for all future tensor types.
  """

  @property
  @abstractmethod
  def rank(self) -> int:
    pass

  @property
  @abstractmethod
  def shape(self) -> Tuple[int, ...]:
    pass

  @abstractmethod
  def transpose(self, axes: Tuple[int, ...]) -> "Tensor":
    pass

  @abstractmethod
  def reshape(self, new_shape: Tuple[int, ...]) -> "Tensor":
    pass

  @abstractmethod
  def permute(self, dims):
    pass

  @abstractmethod
  def conj(self):
    pass

  @abstractmethod
  def contract(self, other: "Tensor", axes: Tuple[List[int], List[int]]) -> "Tensor":
    """maybe name this einsum"""
    pass

  @abstractmethod
  def __add__(self, other: "Tensor"):
    pass

  @abstractmethod
  def __neg__(self):
    pass

  def __sub__(self, other: "Tensor"):
    return self + (-other)

  @abstractmethod
  def __mul__(self, scalar: float) -> "Tensor":
    # TODO: complex?
    pass

  @abstractmethod
  def __matmul__(self, other) -> "Tensor":
    pass

  @abstractmethod
  def ndim(self) -> int:
    pass

  @abstractmethod
  def memory_size(self) -> int:
    raise NotImplementedError("Needs to be implemented for each subclass.")

  def __repr__(self) -> str:
    return f"<{self.__class__.__name__} (rank={self.rank}, shape={self.shape})>"

  @abstractmethod
  def ident(self, k: int) -> "Tensor":
    pass

  @abstractmethod
  def svd(self):
    raise NotImplementedError('Must be implemented in subclass')

  @abstractmethod
  def qr(self, mode:str):
    raise NotImplementedError('Must be implemented in subclass')

  @abstractmethod
  def to_numpy(self):
    raise NotImplementedError('Must be implemented in subclass.')


def primitive_einsum(equation, A: Tensor, B: Tensor):
  import math

  lhs, rhs = equation.replace(" ", "").split("->")
  idx_a, idx_b = lhs.split(",")
  idx_out = rhs

  dim_sizes = {}
  for char, size in zip(idx_a, A.shape):
    dim_sizes[char] = size
  for char, size in zip(idx_b, B.shape):
    dim_sizes[char] = size

  contracting = [c for c in idx_a if c in idx_b]
  free_a = [c for c in idx_a if c not in contracting]
  free_b = [c for c in idx_b if c not in contracting]

  perm_a = [idx_a.index(c) for c in (free_a + contracting)]
  A_perm = A.permute(perm_a)

  perm_b = [idx_b.index(c) for c in (contracting + free_b)]
  B_perm = B.permute(perm_b)

  size_free_a = math.prod(dim_sizes[c] for c in free_a)
  size_free_b = math.prod(dim_sizes[c] for c in free_b)
  size_contract = math.prod(dim_sizes[c] for c in contracting)

  A_2d = A_perm.reshape((size_free_a, size_contract))
  B_2d = B_perm.reshape((size_contract, size_free_b))

  out_2d = A_2d @ (B_2d)

  split_shape = tuple(dim_sizes[c] for c in (free_a + free_b))
  out_nd = out_2d.reshape(split_shape)

  current_out_idx = free_a + free_b
  final_perm = [current_out_idx.index(c) for c in idx_out]

  if final_perm != list(range(len(final_perm))):
    out_final = out_nd.permute(final_perm)
  else:
    out_final = out_nd

  return out_final

class NPTensor(Tensor):
  def __init__(self, data: np.ndarray):
    self.data = np.array(data, dtype=complex)

  @property
  def rank(self) -> int:
    return self.data.ndim

  @property
  def shape(self) -> Tuple[int, ...]:
    return self.data.shape

  def transpose(self, axes: Tuple[int, ...]) -> "NPTensor":
    return NPTensor(np.transpose(self.data, axes))

  def reshape(self, new_shape: Tuple[int, ...]) -> "NPTensor":
    return NPTensor(np.reshape(self.data, new_shape))

  def conj(self):
    return NPTensor(np.conj(self.data))

  def contract(self, other, axes: Tuple[List[int], List[int]]) -> "NPTensor":
    if not isinstance(other, NPTensor):
      raise TypeError("Not a dense tensor.")
    res = np.tensordot(self.data, other.data, axes=axes)
    return NPTensor(res)

  def __add__(self, other) -> "NPTensor":
    return NPTensor(self.data + other.data)

  def __neg__(self):
    return NPTensor(-self.data)

  # def __sub__(self, other):
  #   return NPTensor(self.data)

  def __mul__(self, scalar: float) -> "NPTensor":
    return NPTensor(self.data * scalar)

  def __matmul__(self, other):
    return NPTensor(self.data @ other.data)

  def permute(self, dims):
    return NPTensor(np.transpose(self.data, dims))

  def __eq__(self, other):
    return (self.data == other.data).all

  def memory_size(self) -> int:
    return self.data.nbytes  # is this correct?

  def ident(self, k: int):
    return NPTensor(np.identity(k))

  def ndim(self) -> int:
    pass

  def qr(self, mode):
    return np.linalg.qr(self.data, mode=mode)

  @property
  def ndim_open(self) -> int:
    pass

  @property
  def ndim_aux(self) -> int:
    pass

  @property
  def ndim_internal(self) -> int:
    return self.ndim_open + self.ndim_aux - 3

  def __repr__(self):
    str(self.data)

  def __str__(self):
    return str(self.data)

def ident(n:int) -> NPTensor:
  return NPTensor(np.identity(n))



def run_tests():
  vec1 = NPTensor(np.array([1, 2, 3]))
  vec2 = NPTensor(np.array([4, 5, 6]))
  r_dot = primitive_einsum("i,i->", vec1, vec2)
  expected_dot = np.dot([1, 2, 3], [4, 5, 6])
  print(f"Dot Product Test: {r_dot.data} == {expected_dot}")

  a = NPTensor(np.array([1, 2]))
  b = NPTensor(np.array([3, 4, 5]))
  r_outer = primitive_einsum("i,j->ij", a, b)
  expected_outer = np.outer([1, 2], [3, 4, 5])
  assert np.allclose(r_outer.data, expected_outer)
  print("Outer Product Test: Passed")

  mat = NPTensor(np.random.randn(4, 3))
  vec = NPTensor(np.random.randn(3))
  r_mv = primitive_einsum("ij,j->i", mat, vec)
  expected_mv = mat.data @ vec.data
  assert np.allclose(r_mv.data, expected_mv)
  print("Matrix-Vector Test: Passed")

  A = NPTensor(np.random.randn(3, 5))
  B = NPTensor(np.random.randn(4, 5))
  r_trans = primitive_einsum("ij,kj->ik", A, B)
  expected_trans = A.data @ B.data.T
  print(r_trans.data)
  print(expected_trans)
  assert np.allclose(r_trans.data, expected_trans)
  
  print("Transposed Matmul Test: Passed")

  T1 = NPTensor(np.random.randn(2, 2, 3, 3))
  T2 = NPTensor(np.random.randn(3, 3, 2, 2))
  r_high = primitive_einsum("abjk,jkcd->abcd", T1, T2)

  expected_high = np.einsum("abjk,jkcd->abcd", T1.data, T2.data)
  assert np.allclose(r_high.data, expected_high)
  print("High-Dimensional Fusion Test: Passed")

  mat_diag = NPTensor(np.random.randn(5, 5))
  eye = NPTensor(np.eye(5))
  r_trace = primitive_einsum("ij,ji->", mat_diag, eye)
  expected_trace = np.trace(mat_diag.data)
  assert np.allclose(r_trace.data, expected_trace)
  print(f"Trace Simulation Test: {r_trace.data} == {expected_trace}")

# run_tests()
# 
# class SU2Tensor(Tensor):
#   def __init__(self, k:int, l:int, aux:int, )

if __name__ == "__main__":
  testtensor = NPTensor(np.eye(4))
  test2 = testtensor @ testtensor
  assert test2 == testtensor

  test3 = primitive_einsum("ij,jk->ik", testtensor, testtensor)
  print(test3)

  run_tests()
