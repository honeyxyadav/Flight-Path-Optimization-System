from __future__ import annotations
import math
from typing import List, Sequence, Tuple
EARTH_RADIUS_KM: float = 6371.0088

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1)
	dlambda = math.radians(lon2 - lon1)

	a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return EARTH_RADIUS_KM * c

def _orientation(p: Tuple[float, float], q: Tuple[float, float], r: Tuple[float, float]) -> int:

	px, py = p
	qx, qy = q
	rx, ry = r
	val = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
	if abs(val) < 1e-12:
		return 0
	return 1 if val > 0 else 2

def _on_segment(p: Tuple[float, float], q: Tuple[float, float], r: Tuple[float, float]) -> bool:
	px, py = p
	qx, qy = q
	rx, ry = r
	return min(px, rx) - 1e-12 <= qx <= max(px, rx) + 1e-12 and min(py, ry) - 1e-12 <= qy <= max(py, ry) + 1e-12

def segments_intersect(a1: Tuple[float, float], a2: Tuple[float, float], b1: Tuple[float, float], b2: Tuple[float, float]) -> bool:
	
	o1 = _orientation(a1, a2, b1)
	o2 = _orientation(a1, a2, b2)
	o3 = _orientation(b1, b2, a1)
	o4 = _orientation(b1, b2, a2)

	if o1 != o2 and o3 != o4:
		return True
	if o1 == 0 and _on_segment(a1, b1, a2):
		return True
	if o2 == 0 and _on_segment(a1, b2, a2):
		return True
	if o3 == 0 and _on_segment(b1, a1, b2):
		return True
	if o4 == 0 and _on_segment(b1, a2, b2):
		return True
	return False

def segment_intersects_polygon(
	lat1: float,
	lon1: float,
	lat2: float,
	lon2: float,
	polygon: Sequence[Tuple[float, float]],
) -> bool:
	
	p1 = (lon1, lat1)
	p2 = (lon2, lat2)

	vertices: List[Tuple[float, float]] = [(lon, lat) for lat, lon in polygon]
	n = len(vertices)
	if n < 3:
		return False

	# Edge intersection
	for i in range(n):
		q1 = vertices[i]
		q2 = vertices[(i + 1) % n]
		if segments_intersect(p1, p2, q1, q2):
			return True

	# If either endpoint inside polygon, treat as intersection
	if _point_in_polygon(p1, vertices) or _point_in_polygon(p2, vertices):
		return True

	return False

def _point_in_polygon(point: Tuple[float, float], polygon_xy: Sequence[Tuple[float, float]]) -> bool:
	
	x, y = point
	inside = False
	n = len(polygon_xy)
	for i in range(n):
		x1, y1 = polygon_xy[i]
		x2, y2 = polygon_xy[(i + 1) % n]
		intersects = ((y1 > y) != (y2 > y)) and (
			x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-18) + x1
		)
		if intersects:
			inside = not inside
	return inside

