from fastapi import FastAPI

from app.schemas import CongestionRequest, CongestionResponse
from app.service import CongestionService

app = FastAPI(title="Traffic Congestion Monitor", version="1.0.0")
service = CongestionService()


@app.post("/congestion", response_model=CongestionResponse)
def detect_congestion(request: CongestionRequest) -> CongestionResponse:
    congested_regions = service.detect_congestion(request.observations)
    return CongestionResponse(congested_regions=congested_regions)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
