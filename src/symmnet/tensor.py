from symmnet.fusiontree import FusionTree, OpenEdge, InternalEdge, label
import symmnet.symmetry as symmetry
from symmnet.symmetry import sector
import numpy as np
from typing import Any


# For now just directly copy the structure from the paper.
class SymmetricTensor:
  def __init__(
    self,
    sym: symmetry.Symmetry,
    listOfOpenEdges: list[OpenEdge],
    listOfInternalEdges: list[InternalEdge],
    # listOfDegeneracyTensors: list[np.ndarray],
    listOfDegeneracyTensors: dict[Any, np.ndarray],
    listOfNodes: list[Any],  # TODO
    listOfDirections: list[Any],
  ):
    self.sym = sym
    self.listOfOpenEdges = listOfOpenEdges
    self.listOfInternalEdges = listOfInternalEdges
    self.listOfDegeneracyTensors = listOfDegeneracyTensors
    self.fusionTree = FusionTree(self.listOfOpenEdges, self.listOfInternalEdges, listOfNodes, listOfDirections, self.sym)
    self.nOpen = len(self.listOfOpenEdges)
    self.nInternal = len(self.listOfInternalEdges)
    self.nAux = None  # TODO
    self.listOfChargeSectors = self.fusionTree.determine_internal_charge_sectors()
    self.listOfDegeneracyTensors = {self._sector_key(s): t for s, t in zip(self.listOfChargeSectors, listOfDegeneracyTensors)}

  @staticmethod
  def _sector_key(sector_dict: dict) -> frozenset:
    """Makes a sector a hashable key as sector is a dict (assigment (is this neceesary?))"""
    return frozenset(sector_dict.items())

  # This has to be here? or make this a function in symmetry?
  def _get_f_symbol(self, old_taus, old_sector, new_sector, edge_id):
    node1, node2 = old_taus[0], old_taus[1]

    a_name, b_name = [leg for leg in node1 if leg != edge_id]
    c_name, d_name = [leg for leg in node2 if leg != edge_id]

    a = old_sector[a_name]
    b = old_sector[b_name]
    c = old_sector[c_name]
    d = old_sector[d_name]

    e = old_sector[edge_id]
    f = new_sector[edge_id]

    return self.sym.F_symbol(a, b, c, d, e, f)

  def _get_r_symbol(self, node, sector):
    a_name, b_name, c_name = node
    a = sector[a_name]
    b = sector[b_name]
    c = sector[c_name]

    return self.sym.R_symbol(a, b, c)

  def fmove(self, edge_id: label):
    old_charge_sectors = self.listOfChargeSectors
    # old_degeneracy_tensors = self.listOfDegeneracyTensors
    old_taus, _ = self.fusionTree.get_node_context(edge_id)

    self.fusionTree.fmove(edge_id)

    new_charge_sectors = self.fusionTree.determine_internal_charge_sectors()
    new_degeneracy_tensors = {}
    for new_sector in new_charge_sectors:
      new_tensor = None
      for old_sector in old_charge_sectors:
        if all(old_sector[k] == v for k, v in new_sector.items() if k != edge_id):
          old_tensor = self.listOfDegeneracyTensors[self._sector_key(old_sector)]
          if new_tensor is None:
            new_tensor = np.zeros_like(old_tensor)
          weight = self._get_f_symbol(old_taus, old_sector, new_sector, edge_id)
          new_tensor += weight * old_tensor
      if new_tensor is None:
        raise RuntimeError(f"No contributing prior sectors found for new sector {new_sector}")
      new_degeneracy_tensors[self._sector_key(new_sector)] = new_tensor

    self.listOfChargeSectors = new_charge_sectors
    self.listOfDegeneracyTensors = new_degeneracy_tensors

  def rmove(self, node_id: int):
    old_node = self.fusionTree.nodes[node_id]
    charge_sectors = self.fusionTree.determine_internal_charge_sectors()  # Is this necessary as its a dict?

    self.fusionTree.rmove(node_id)

    new_degeneracy_tensors = {}
    for sect in charge_sectors:
      weight = self._get_r_symbol(old_node, sect)
      old_tensor = self.listOfDegeneracyTensors[self._sector_key(sect)]
      new_degeneracy_tensors[self._sector_key(sect)] = weight * old_tensor

    self.listOfChargeSectors = charge_sectors
    self.listOfDegeneracyTensors = new_degeneracy_tensors

  # TODO i really dont like this, as the seach is quite heavy on performance.
  def _swap_adjacent(self, leg1, leg2: label):
    path_edges = self.fusionTree.get_path_between_legs(leg1, leg2)
    for internal_edge in path_edges:
      print(f"-- f-move on {internal_edge}")
      self.fmove(internal_edge)

    common_node_id = self.fusionTree.get_parent_node(leg1, leg2)

    self.rmove(common_node_id)

  def permute(self, target_order: list[label]):  # TODO find optimal ordering for this from tehsis or paper
    current_order = [edge.name for edge in self.listOfOpenEdges]
    n = len(current_order)

    for i in range(n):
      for j in range(0, n - i - 1):
        curr_a, curr_b = current_order[j], current_order[j + 1]
        if target_order.index(curr_a) > target_order.index(curr_b):
          self._swap_adjacent(curr_a, curr_b)
          print(f"--- swapping {curr_a} with {curr_b}.")

          current_order[j], current_order[j + 1] = current_order[j + 1], current_order[j]


def test_fmove_transformation():
  from symmnet.fusiontree import NodeType

  sym = symmetry.Fib()

  open_edges = [
    OpenEdge(name=-1, number=1, direction=+1, irreps=[(1, 1)]),
    OpenEdge(name=-2, number=2, direction=+1, irreps=[(1, 1)]),
    OpenEdge(name=-3, number=3, direction=+1, irreps=[(1, 1)]),
    OpenEdge(name=-4, number=4, direction=+1, irreps=[(1, 1)]),
  ]

  internal_edges = [InternalEdge(name="internal_1", number=1)]

  nodes = [(-1, -2, "internal_1"), ("internal_1", -3, -4)]
  directions = [NodeType.fusion, NodeType.fusion]

  tensor = SymmetricTensor(
    sym=sym,
    listOfOpenEdges=open_edges,
    listOfInternalEdges=internal_edges,
    listOfDegeneracyTensors={},  # This ought to be a dict? or do we assume a sort?
    listOfNodes=nodes,
    listOfDirections=directions,
  )

  # Like in the goden chain
  print(f"Found {len(tensor.listOfChargeSectors)} initial charge sectors.")
  for idx, sector in enumerate(tensor.listOfChargeSectors):
    print(f"  Sector {idx}: {sector}")
    if idx == 0:
      dummy_array = np.array([-1.0])
    else:
      dummy_array = np.array([0.0])
    tensor.listOfDegeneracyTensors[SymmetricTensor._sector_key(sector)] = dummy_array

  # edge_to_mutate = "internal_1"

  old_sectors = list(tensor.listOfChargeSectors)
  print(tensor.listOfDegeneracyTensors)

  # tensor.fmove(edge_to_mutate)

  tensor.permute([-1, -3, -2, -4])

  print(f"New tree nodes: {tensor.fusionTree.nodes}")
  print(f"Found {len(tensor.listOfChargeSectors)} new charge sectors.")

  for idx, new_sector in enumerate(tensor.listOfChargeSectors):
    print(f"\n  New Sector {idx}: {new_sector}")
    new_array = tensor.listOfDegeneracyTensors[SymmetricTensor._sector_key(new_sector)]
    print(f"  Resulting Degeneracy Array:\n{new_array}")


if __name__ == "__main__":
  test_fmove_transformation()
