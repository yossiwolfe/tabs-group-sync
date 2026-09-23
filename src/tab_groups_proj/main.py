from datetime import datetime
from fastapi import FastAPI, Query, status
from .database import init_db
from typing import Optional

init_db()

app = FastAPI(
    title="Tabs Group API",
    description="Syncing tab groups across multiple devices in real time",
    version="0.0.1"
)

@app.get(
    "/",
    summary="Root Health Check",
    status_code=status.HTTP_200_OK,
    tags=["System"]
)
def read_root():
    """
    **Check System Availability**

    This endpoint serves as a basic health check for the API.
    """
    return { "message": "Hey there!" }

@app.get(
    "/groups",
    summary="Sync Tab Groups",
    tags=["Groups"],
    status_code=status.HTTP_200_OK
)
def get_groups(
    since: Optional[datetime] = Query(
        default=None,
        description="Filter groups modified after this timestamp. Expects an ISO 8601 string (e.g., 2026-09-23T12:00:00Z)."
    ),
):
    """
    Retrieve tab groups. If 'since' is provided, only show tab groups updated since that time.
    """
    return {
        "sync_time_received": since,
        "groups": []
    }