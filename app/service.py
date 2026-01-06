from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence

from app.schemas import Coordinate, CongestionRegion, VehicleObservation


@dataclass
class ClusterResult:
    centroid: Coordinate
    vehicle_ids: List[str]
    average_speed: Optional[float]
    observations: Sequence[VehicleObservation]


class CongestionService:
    def __init__(
        self,
        radius_meters: float = 50.0,
        minimum_cluster_size: int = 3,
        high_vehicle_threshold: int = 8,
        medium_vehicle_threshold: int = 3,
        high_speed_threshold: float = 5,
        medium_speed_threshold: float = 15,
    ):
        self.radius_meters = radius_meters
        self.minimum_cluster_size = minimum_cluster_size
        self.high_vehicle_threshold = high_vehicle_threshold
        self.medium_vehicle_threshold = medium_vehicle_threshold
        self.high_speed_threshold = high_speed_threshold
        self.medium_speed_threshold = medium_speed_threshold

    def detect_congestion(self, observations: Sequence[VehicleObservation]) -> List[CongestionRegion]:
        clusters = self._cluster_observations(observations)
        congested_regions: List[CongestionRegion] = []

        for index, cluster in enumerate(clusters):
            congestion_level = self._derive_congestion_level(
                len(cluster.vehicle_ids), cluster.average_speed
            )
            boundary = self._build_boundary(cluster.observations)
            region = CongestionRegion(
                region_id=index + 1,
                centroid=cluster.centroid,
                boundary=boundary,
                vehicle_ids=cluster.vehicle_ids,
                congestion_level=congestion_level,
            )
            congested_regions.append(region)

        return congested_regions

    def _cluster_observations(
        self, observations: Sequence[VehicleObservation]
    ) -> List[ClusterResult]:
        clusters: List[List[VehicleObservation]] = []
        visited = [False] * len(observations)

        for index in range(len(observations)):
            if visited[index]:
                continue

            visited[index] = True
            current_cluster = [observations[index]]
            neighbors = self._find_neighbors(index, observations, visited)

            queue = list(neighbors)
            for neighbor_index in neighbors:
                visited[neighbor_index] = True

            while queue:
                neighbor_index = queue.pop()
                current_cluster.append(observations[neighbor_index])
                extended_neighbors = self._find_neighbors(
                    neighbor_index, observations, visited
                )
                for extended_index in extended_neighbors:
                    if not visited[extended_index]:
                        visited[extended_index] = True
                        queue.append(extended_index)

            if len(current_cluster) >= self.minimum_cluster_size:
                clusters.append(current_cluster)

        results: List[ClusterResult] = []
        for cluster in clusters:
            centroid = self._calculate_centroid(cluster)
            vehicle_ids = [item.vehicle_id for item in cluster]
            average_speed = self._average_speed(cluster)
            results.append(
                ClusterResult(
                    centroid=centroid,
                    vehicle_ids=vehicle_ids,
                    average_speed=average_speed,
                    observations=cluster,
                )
            )

        return results

    def _find_neighbors(
        self,
        source_index: int,
        observations: Sequence[VehicleObservation],
        visited: Sequence[bool],
    ) -> List[int]:
        neighbors: List[int] = []
        source = observations[source_index]
        for index, candidate in enumerate(observations):
            if visited[index] or index == source_index:
                continue
            distance = self._haversine_distance(
                source.coordinate.latitude,
                source.coordinate.longitude,
                candidate.coordinate.latitude,
                candidate.coordinate.longitude,
            )
            if distance <= self.radius_meters:
                neighbors.append(index)
        return neighbors

    def _calculate_centroid(self, cluster: Sequence[VehicleObservation]) -> Coordinate:
        latitude_sum = sum(item.coordinate.latitude for item in cluster)
        longitude_sum = sum(item.coordinate.longitude for item in cluster)
        count = len(cluster)
        return Coordinate(latitude=latitude_sum / count, longitude=longitude_sum / count)

    def _average_speed(self, cluster: Sequence[VehicleObservation]) -> Optional[float]:
        speeds = [item.speed_kph for item in cluster if item.speed_kph is not None]
        if not speeds:
            return None
        return sum(speeds) / len(speeds)

    def _derive_congestion_level(
        self, cluster_size: int, average_speed: Optional[float]
    ) -> str:
        # Priority on traffic size, then speed; conservative defaults when speed unknown
        if cluster_size >= self.high_vehicle_threshold or (
            average_speed is not None and average_speed < self.high_speed_threshold
        ):
            return "high"
        if cluster_size >= self.medium_vehicle_threshold or (
            average_speed is not None and average_speed < self.medium_speed_threshold
        ):
            return "medium"
        return "low"

    def _build_boundary(
        self, cluster: Sequence[VehicleObservation]
    ) -> List[Coordinate]:
        points = [
            (ob.coordinate.longitude, ob.coordinate.latitude) for ob in cluster
        ]
        unique_points = sorted(set(points))

        # Fallback for degenerate cases
        if len(unique_points) == 1:
            lon, lat = unique_points[0]
            return [Coordinate(latitude=lat, longitude=lon)]
        if len(unique_points) == 2:
            (lon1, lat1), (lon2, lat2) = unique_points
            return [
                Coordinate(latitude=lat1, longitude=lon1),
                Coordinate(latitude=lat2, longitude=lon1),
                Coordinate(latitude=lat2, longitude=lon2),
                Coordinate(latitude=lat1, longitude=lon2),
            ]

        def cross(
            origin: tuple[float, float],
            a: tuple[float, float],
            b: tuple[float, float],
        ) -> float:
            return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (
                b[0] - origin[0]
            )

        lower: List[tuple[float, float]] = []
        for point in unique_points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
                lower.pop()
            lower.append(point)

        upper: List[tuple[float, float]] = []
        for point in reversed(unique_points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
                upper.pop()
            upper.append(point)

        hull = lower[:-1] + upper[:-1]
        return [
            Coordinate(latitude=lat, longitude=lon) for lon, lat in hull
        ]

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        radius_earth_m = 6371000
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_earth_m * c
