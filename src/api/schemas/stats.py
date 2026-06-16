"""Pydantic schemas for stats and dashboard."""

from pydantic import BaseModel
from typing import Dict, List


class StatsResponse(BaseModel):
    labels: List[str]
    total_requests: List[int]
    failed_requests: List[int]
    rate_limited_requests: List[int]
    model_requests: Dict[str, List[int]]
    model_ttfb_times: Dict[str, List[float]]
    model_total_times: Dict[str, List[float]]


class TotalCountsResponse(BaseModel):
    success: int
    failed: int
