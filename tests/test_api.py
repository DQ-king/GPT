from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_congestion_endpoint_returns_regions():
    payload = {
        "observations": [
            {
                "vehicle_id": "A",
                "coordinate": {"latitude": 40.0, "longitude": -74.0},
                "speed_kph": 8,
            },
            {
                "vehicle_id": "B",
                "coordinate": {"latitude": 40.0003, "longitude": -74.0002},
                "speed_kph": 9,
            },
            {
                "vehicle_id": "C",
                "coordinate": {"latitude": 40.0004, "longitude": -74.0003},
                "speed_kph": 7,
            },
        ]
    }

    response = client.post("/congestion", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "congested_regions" in body
    assert len(body["congested_regions"]) == 1
    region = body["congested_regions"][0]
    assert set(region["vehicle_ids"]) == {"A", "B", "C"}
    assert region["congestion_level"] == "medium"
    assert "boundary" in region
    assert len(region["boundary"]) >= 3
