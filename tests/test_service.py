from app.schemas import Coordinate, VehicleObservation
from app.service import CongestionService


def test_detects_single_cluster_with_centroid_and_level():
    service = CongestionService(radius_meters=60, minimum_cluster_size=3)
    observations = [
        VehicleObservation(vehicle_id="A", coordinate=Coordinate(latitude=40.0, longitude=-74.0), speed_kph=5),
        VehicleObservation(vehicle_id="B", coordinate=Coordinate(latitude=40.0003, longitude=-74.0003), speed_kph=6),
        VehicleObservation(vehicle_id="C", coordinate=Coordinate(latitude=40.0005, longitude=-74.0005), speed_kph=7),
    ]

    regions = service.detect_congestion(observations)

    assert len(regions) == 1
    region = regions[0]
    assert set(region.vehicle_ids) == {"A", "B", "C"}
    assert region.congestion_level == "medium"
    assert 39.999 < region.centroid.latitude < 40.001
    assert -74.001 < region.centroid.longitude < -73.999
    assert len(region.boundary) >= 3
    assert all(-90 <= point.latitude <= 90 for point in region.boundary)
    assert all(-180 <= point.longitude <= 180 for point in region.boundary)


def test_excludes_small_groups_below_threshold():
    service = CongestionService(radius_meters=60, minimum_cluster_size=3)
    observations = [
        VehicleObservation(vehicle_id="A", coordinate=Coordinate(latitude=40.0, longitude=-74.0)),
        VehicleObservation(vehicle_id="B", coordinate=Coordinate(latitude=40.0, longitude=-74.0004)),
    ]

    regions = service.detect_congestion(observations)

    assert regions == []


def test_detects_multiple_clusters():
    service = CongestionService(radius_meters=60, minimum_cluster_size=3)
    observations = [
        VehicleObservation(vehicle_id="A", coordinate=Coordinate(latitude=40.0, longitude=-74.0), speed_kph=30),
        VehicleObservation(vehicle_id="B", coordinate=Coordinate(latitude=40.0003, longitude=-74.0002), speed_kph=28),
        VehicleObservation(vehicle_id="C", coordinate=Coordinate(latitude=40.0004, longitude=-74.0004), speed_kph=29),
        VehicleObservation(vehicle_id="D", coordinate=Coordinate(latitude=41.0, longitude=-75.0), speed_kph=3),
        VehicleObservation(vehicle_id="E", coordinate=Coordinate(latitude=41.0003, longitude=-75.0001), speed_kph=4),
        VehicleObservation(vehicle_id="F", coordinate=Coordinate(latitude=41.0004, longitude=-75.0003), speed_kph=5),
        VehicleObservation(vehicle_id="G", coordinate=Coordinate(latitude=41.0005, longitude=-75.0005), speed_kph=4),
    ]

    regions = service.detect_congestion(observations)

    assert len(regions) == 2
    levels = {region.region_id: region.congestion_level for region in regions}
    assert set(levels.values()) == {"medium", "high"}
