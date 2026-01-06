from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator


class Coordinate(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")

    @validator("latitude")
    def latitude_range(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 and 90 degrees")
        return value

    @validator("longitude")
    def longitude_range(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 and 180 degrees")
        return value


class VehicleObservation(BaseModel):
    vehicle_id: str = Field(..., description="Unique identifier for the vehicle")
    coordinate: Coordinate
    speed_kph: Optional[float] = Field(
        None, description="Speed in kilometers per hour"
    )
    heading_degrees: Optional[float] = Field(
        None, description="Heading direction in degrees from true north"
    )

    @validator("speed_kph")
    def speed_positive(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value < 0:
            raise ValueError("speed cannot be negative")
        return value

    @validator("heading_degrees")
    def heading_range(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not 0 <= value <= 360:
            raise ValueError("heading must be between 0 and 360 degrees")
        return value


class CongestionRequest(BaseModel):
    observations: List[VehicleObservation] = Field(
        ..., description="List of vehicle observations"
    )

    @root_validator
    def require_observations(cls, values: dict) -> dict:
        observations = values.get("observations")
        if not observations:
            raise ValueError("observations cannot be empty")
        return values


class CongestionRegion(BaseModel):
    region_id: int
    centroid: Coordinate
    boundary: List[Coordinate] = Field(
        ..., description="Convex hull boundary of the congested region"
    )
    vehicle_ids: List[str]
    congestion_level: str


class CongestionResponse(BaseModel):
    congested_regions: List[CongestionRegion]
