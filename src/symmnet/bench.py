from typing import Literal, Optional, TypedDict
import numpy as np

BackendName = Literal["Numpy", "Tree"]


class RawRecord(TypedDict):
  backed_name: BackendName
  run: int
  path: str
  exception: Optional[str]


class ResultRecord(RawRecord):
  system_size : int # What to collect here?
  total_time_ms: int
  contractions: int


def geomean(xs: list[float]) -> float:
  logs = [np.log(x) for x in xs if x > 0]
  return np.exp(sum(logs) / len(logs)) if logs else 0.0


def geomean_speedup(a: float, b: float) -> float:
  a = float(a)
  b = float(b)
  assert a >= 0
  assert b >= 0
  if a == 0:
    return 0.0
  if b == 0:
    return float("inf")
  return a / b
