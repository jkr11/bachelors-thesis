from symmnet.core import Tensor
import symmnet.core as core
import numpy as np

def mps_vdot(Alist:list[Tensor], Blist:list[Tensor]) -> Tensor:
  assert len(Alist) == len(Blist)
  d = len(Alist)

  R = core.primitive_einsum('ijk,ilk -> jl', Blist[d-1], Alist[d-1].conj())
  for l in range(d-2, -1, -1):
    Rl = core.primitive_einsum('nij,kj -> kni', Alist[l].conj(), R)
    R = core.primitive_einsum("nij,jnk -> ik", Blist[l], Rl)
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

def mps_to_full_tensor(Alist:list[Tensor]):
  assert Alist[0].ndim == 3 and Alist[0].shape[1] == 1
  T = Alist[0].reshape((Alist[0].shape[0], Alist[0].shape[2]))
  for i in range(1,len(Alist)):
    pass # TODO: core.tensordot

def _orthonormalize_left(A:Tensor, An:Tensor) -> tuple[Tensor,Tensor]:
  n, D_left, D_right = A.shape
  A = A.reshape((n * D_left, D_right))
  Q, R = A.qr(mode='reduced')
  A = Q.reshape( (n, D_left, Q.shape[1]))
  An = core.primitive_einsum("ij,njl->nil", R, An)
  return A, An

def mps_orthonormalize_left(Alist:list[Tensor]) -> float:
  """
  Left-orthonormalize a MPS using QR decompositions.
  The list of tensors in `Alist` are updated in-place.

  Returns the overall norm of the original MPS. (The updated MPS has norm 1.)
  """
  Alist.append(np.array([[[1.0]]])) # What would this be if it was symmetric? the 3 legged dummy CG tensor?
  d = len(Alist) - 1
  for l in range(d):
    Alist[l], Alist[l + 1] = _orthonormalize_left(Alist[l], Alist[l + 1])

  if Alist[-1][0, 0, 0] < 0:
    Alist[-2] = -Alist[-2]
    Alist[-1] = -Alist[-1]

  norm = float(abs(Alist[-1][0, 0, 0]))
  Alist.pop()

  return norm
