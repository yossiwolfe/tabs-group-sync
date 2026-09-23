from fastapi import FastAPI, status

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