import argparse
from typing import List

from flight_opt.constraints import RoutingConfig
from flight_opt.data.sample_data import (
	AIRPORTS,
	NO_FLY_ZONES,
	WEATHER_EDGE_PENALTY_KM,
	PREFERRED_HUBS,
)
from flight_opt.routing import find_optimal_route
from flight_opt.visualize import plot_route


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Flight Path Optimization CLI")
	p.add_argument("--from", dest="origin", required=True, help="Origin IATA code")
	p.add_argument("--to", dest="destination", required=True, help="Destination IATA code")
	p.add_argument("--max-leg", type=float, default=6000.0, help="Maximum leg distance (km)")
	p.add_argument("--hub", action="append", default=None, help="Preferred hub (repeatable)")
	p.add_argument("--hub-bonus", type=float, default=-50.0, help="Bonus (negative cost in km) per leg touching a hub")
	p.add_argument("--no-fly-off", action="store_true", help="Disable sample no-fly zones")
	p.add_argument("--no-weather", action="store_true", help="Disable sample weather penalties")
	p.add_argument("--plot", default=None, help="Output image path to save plot")
	p.add_argument("--no-show", action="store_true", help="Do not display plot window")
	return p.parse_args()


def main() -> None:
	args = parse_args()
	preferred_hubs = set(args.hub if args.hub else PREFERRED_HUBS)
	config = RoutingConfig(
		max_leg_km=args.max_leg,
		preferred_hubs=preferred_hubs,
		hub_bonus_km=args.hub_bonus,
		no_fly_zones=[] if args.no_fly_off else NO_FLY_ZONES,
		weather_edge_penalty_km={} if args.no_weather else WEATHER_EDGE_PENALTY_KM,
	)

	result = find_optimal_route(AIRPORTS, args.origin.upper(), args.destination.upper(), config)
	print(f"Path: {' -> '.join(result.path)}")
	print(f"Total distance: {result.total_distance_km:.0f} km")
	print(f"Total cost: {result.total_cost_km:.0f} km")
	for i, leg in enumerate(result.legs, 1):
		print(
			f"Leg {i}: {leg.origin}->{leg.destination} | d={leg.distance_km:.0f} km, "
			f"weather=+{leg.weather_penalty_km:.0f} km, hub={leg.hub_bonus_km:.0f} km, cost={leg.total_cost_km:.0f} km"
		)

	if args.plot or not args.no_show:
		plot_route(
			AIRPORTS,
			result.path,
			NO_FLY_ZONES if not args.no_fly_off else [],
			title=f"{args.origin.upper()} to {args.destination.upper()}",
			outfile=args.plot,
			show=(not args.no_show),
		)


if __name__ == "__main__":
	main()

