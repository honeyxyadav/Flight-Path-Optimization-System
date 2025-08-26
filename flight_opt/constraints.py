from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Sequence, Set, Tuple

@dataclass(frozen=True)
class NoFlyZone:
	name: str
	polygon: Sequence[Tuple[float, float]]  # sequence of (lat, lon)

@dataclass
class RoutingConfig:
	
	max_leg_km: float
	preferred_hubs: Set[str] = field(default_factory=set)
	hub_bonus_km: float = 0.0
	no_fly_zones: Sequence[NoFlyZone] = field(default_factory=list)
	weather_edge_penalty_km: Mapping[frozenset, float] = field(default_factory=dict)

def edge_key(a: str, b: str) -> frozenset:
	return frozenset({a, b})

