"""Statistics and monitoring routes."""

from typing import Callable
from fastapi import FastAPI, Query

from ..schemas.stats import StatsResponse, TotalCountsResponse


def register_stats_routes(
    app: FastAPI,
    get_stats_by_time_range: Callable,
    get_total_counts: Callable,
):
    """Register statistics routes."""

    @app.get("/api/stats", response_model=StatsResponse)
    async def api_get_stats(time_range: str = Query("24h", regex="^(24h|7d|30d)$")):
        stats = await get_stats_by_time_range(time_range)
        return StatsResponse(**stats)

    @app.get("/api/stats/totals", response_model=TotalCountsResponse)
    async def api_get_total_counts():
        success, failed = await get_total_counts()
        return TotalCountsResponse(success=success, failed=failed)
