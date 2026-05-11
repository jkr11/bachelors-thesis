from symmnet.core import Tensor
import symmnet.core as core
import numpy as np

def mps_vdot(Alist:list[Tensor], Blist:list[Tensor]) -> Tensor:
  assert len(Alist) == len(Blist)
  d = len(Alist)

  R = Tensor.einsum('ijk,ilk -> jl', Blist[d-1], Alist[d-1].conj())
  for l in range(d-2, -1, -1):
    Rl = Tensor.einsum('nij,kj -> kni', Alist[l].conj(), R)
    R = Tensor.einsum("nij,jnk -> ik", Blist[l], Rl)
  return R

def is_left_orthonormal(A:Tensor) -> bool:
  s = A.shape
  assert len(s) == 3
  A = A.reshape((s[0] * s[1], s[2]))
  return np.allclose(A.conj().transpose().data @ A, core.ident(s[2]).data) # TODO: make this np like.

def is_right_orthonormal(A:Tensor) -> bool:
  """
  Test whether a MPS tensor `A` is right-orthonormal.
  """
  return is_left_orthonormal(A.transpose((0, 2, 1)))