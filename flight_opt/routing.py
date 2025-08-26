from __future__ import annotations
from dataclasses import dataclass
from typing import List, Mapping, Tuple
import networkx as nx
from .geo import haversine_distance_km, segment_intersects_polygon
from .constraints import RoutingConfig, edge_key


@dataclass
class RouteLeg:
	origin: str
	destination: str
	distance_km: float
	weather_penalty_km: float
	hub_bonus_km: float
	total_cost_km: float


@dataclass
class RouteResult:
	path: List[str]
	legs: List[RouteLeg]
	total_distance_km: float
	total_cost_km: float


class AirportGraphBuilder:
	def __init__(
		self,
		airports: Mapping[str, Tuple[str, float, float]],
		config: RoutingConfig,
	) -> None:
		self.airports = airports
		self.config = config

	def build_graph(self) -> nx.Graph:
		g = nx.Graph()
		for code, (name, lat, lon) in self.airports.items():
			g.add_node(code, name=name, lat=lat, lon=lon)

		codes = list(self.airports.keys())
		for i in range(len(codes)):
			a = codes[i]
			_, alat, alon = self.airports[a]
			for j in range(i + 1, len(codes)):
				b = codes[j]
				_, blat, blon = self.airports[b]
				d = haversine_distance_km(alat, alon, blat, blon)
				if d <= self.config.max_leg_km and self._edge_allowed(alat, alon, blat, blon):
					weather = float(self.config.weather_edge_penalty_km.get(edge_key(a, b), 0.0))
					# Hub bonus applies if either endpoint is a preferred hub
					hub_bonus = 0.0
					if a in self.config.preferred_hubs:
						hub_bonus += self.config.hub_bonus_km
					if b in self.config.preferred_hubs:
						hub_bonus += self.config.hub_bonus_km
					cost = max(1e-6, d + weather + hub_bonus)
					g.add_edge(a, b, distance_km=d, weather_penalty_km=weather, hub_bonus_km=hub_bonus, weight=cost)
		return g

	def _edge_allowed(self, alat: float, alon: float, blat: float, blon: float) -> bool:
		for zone in self.config.no_fly_zones:
			if segment_intersects_polygon(alat, alon, blat, blon, zone.polygon):
				return False
		return True


def _heuristic(g: nx.Graph, a: str, b: str) -> float:
	lat1 = g.nodes[a]["lat"]
	lon1 = g.nodes[a]["lon"]
	lat2 = g.nodes[b]["lat"]
	lon2 = g.nodes[b]["lon"]
	return haversine_distance_km(lat1, lon1, lat2, lon2)


def find_optimal_route(
	airports: Mapping[str, Tuple[str, float, float]],
	origin: str,
	destination: str,
	config: RoutingConfig,
) -> RouteResult:
	builder = AirportGraphBuilder(airports, config)
	g = builder.build_graph()

	if origin not in g or destination not in g:
		raise ValueError("Origin or destination airport not found in dataset")

	try:
		path = nx.astar_path(g, origin, destination, heuristic=lambda u, v: _heuristic(g, u, v), weight="weight")
	except nx.NetworkXNoPath as exc:
		raise ValueError("No feasible route under current constraints") from exc

	legs: List[RouteLeg] = []
	total_distance = 0.0
	total_cost = 0.0
	for a, b in zip(path[:-1], path[1:]):
		edge = g.edges[a, b]
		leg = RouteLeg(
			origin=a,
			destination=b,
			distance_km=float(edge["distance_km"]),
			weather_penalty_km=float(edge.get("weather_penalty_km", 0.0)),
			hub_bonus_km=float(edge.get("hub_bonus_km", 0.0)),
			total_cost_km=float(edge["weight"]),
		)
		legs.append(leg)
		total_distance += leg.distance_km
		total_cost += leg.total_cost_km

	return RouteResult(path=path, legs=legs, total_distance_km=total_distance, total_cost_km=total_cost)

