from __future__ import annotations
from typing import Mapping, Sequence, Tuple
import matplotlib.pyplot as plt
from .constraints import NoFlyZone

def plot_route(
	airports: Mapping[str, Tuple[str, float, float]],
	path: Sequence[str],
	no_fly_zones: Sequence[NoFlyZone] = (),
	title: str = "Flight Path",
	outfile: str | None = None,
	show: bool = True,
):
	fig, ax = plt.subplots(figsize=(10, 5))
	ax.set_title(title)
	ax.set_xlabel("Longitude")
	ax.set_ylabel("Latitude")
	ax.grid(True, linestyle=":", alpha=0.5)

	# Plot no-fly zones
	for zone in no_fly_zones:
		lats = [lat for lat, _ in zone.polygon] + [zone.polygon[0][0]]
		lons = [lon for _, lon in zone.polygon] + [zone.polygon[0][1]]
		ax.fill(lons, lats, color="red", alpha=0.2, label=f"No-Fly: {zone.name}")

	# Plot airports
	lats = [airports[c][1] for c in airports]
	lons = [airports[c][2] for c in airports]
	ax.scatter(lons, lats, s=20, c="black", alpha=0.7, zorder=3)
	for code, (name, lat, lon) in airports.items():
		ax.text(lon + 0.3, lat + 0.3, code, fontsize=8)

	# Plot route path
	if path and len(path) >= 2:
		route_lats = [airports[c][1] for c in path]
		route_lons = [airports[c][2] for c in path]
		ax.plot(route_lons, route_lats, "-o", color="blue", linewidth=2, markersize=5, zorder=4, label="Route")

	ax.set_xlim(-180, 180)
	ax.set_ylim(-90, 90)
	ax.legend(loc="upper right")

	fig.tight_layout()
	if outfile:
		fig.savefig(outfile, dpi=150)
	if show:
		plt.show()
	plt.close(fig)

