"""Sample dataset: airports, hubs, no-fly zones, weather penalties.
"""
from __future__ import annotations
from typing import Dict, Sequence, Tuple
from ..constraints import NoFlyZone

# Airport code -> (name, lat, lon)
AIRPORTS: Dict[str, Tuple[str, float, float]] = {
	"JFK": ("New York JFK", 40.6413, -73.7781),
	"LHR": ("London Heathrow", 51.4700, -0.4543),
	"CDG": ("Paris CDG", 49.0097, 2.5479),
	"FRA": ("Frankfurt", 50.0379, 8.5622),
	"ATL": ("Atlanta Hartsfield-Jackson", 33.6407, -84.4277),
	"ORD": ("Chicago O'Hare", 41.9742, -87.9073),
	"LAX": ("Los Angeles", 33.9416, -118.4085),
	"SFO": ("San Francisco", 37.6213, -122.3790),
	"DFW": ("Dallas/Fort Worth", 32.8998, -97.0403),
	"DEN": ("Denver", 39.8561, -104.6737),
	"SEA": ("Seattle/Tacoma", 47.4502, -122.3088),
	"MIA": ("Miami", 25.7959, -80.2871),
	"YYZ": ("Toronto Pearson", 43.6777, -79.6248),
	"MAD": ("Madrid Barajas", 40.4983, -3.5676),
	"DXB": ("Dubai", 25.2532, 55.3657),
	"DEL": ("Delhi Indira Gandhi", 28.5562, 77.1000),
	# India regional
	"BOM": ("Mumbai Chhatrapati Shivaji", 19.0896, 72.8656),
	"BLR": ("Bengaluru Kempegowda", 13.1989, 77.7063),
	"MAA": ("Chennai International", 12.9941, 80.1709),
	"HYD": ("Hyderabad Rajiv Gandhi", 17.2403, 78.4294),
	"CCU": ("Kolkata Netaji Subhas Chandra Bose", 22.6547, 88.4467),
	"AMD": ("Ahmedabad Sardar Vallabhbhai Patel", 23.0746, 72.6347),
}

# Define a synthetic no-fly polygon over a small Atlantic area
NO_FLY_ZONES: Sequence[NoFlyZone] = [
	NoFlyZone(
		name="Atlantic Box",
		polygon=[
			(35.0, -45.0),
			(45.0, -45.0),
			(45.0, -30.0),
			(35.0, -30.0),
		],
	)
]

# Weather penalties in km per edge (symmetric via frozenset)
from ..constraints import edge_key

WEATHER_EDGE_PENALTY_KM = {
	edge_key("JFK", "LHR"): 150.0,
	edge_key("JFK", "CDG"): 120.0,
	edge_key("LAX", "SFO"): 30.0,
	edge_key("ORD", "DEN"): 40.0,
	# India examples (synthetic)
	edge_key("DEL", "BOM"): 20.0,
	edge_key("BLR", "MAA"): 10.0,
}

# Preferred hub examples
PREFERRED_HUBS = {"ATL", "FRA", "DXB", "DEL"}
