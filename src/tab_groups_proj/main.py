from datetime import datetime
import uuid
from fastapi import FastAPI, Query, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import init_db, get_db
from .models import TabGroup
from . import schemas
from typing import Optional, List

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
    tags=["System"],
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
    tags=["Group"],
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.TabGroupRead]
)
def get_groups(
    since: Optional[datetime] = Query(
        default=None,
        description="Filter groups modified after this timestamp. Expects an ISO 8601 string (e.g., 2026-09-23T12:00:00Z)."
    ),
    db: Session = Depends(get_db)
):
    """
    Retrieve tab groups. If 'since' is provided, only show tab groups updated since that time.
    """

    statement = select(TabGroup).where(TabGroup.deleted == False)

    if since is not None:
        clean_since = since.strftime("%Y-%m-%d %H:%M:%S") # there are weird millisecond artifacts that make this necessary
        statement = statement.where(TabGroup.updated_at >= clean_since)

    return db.scalars(statement).all()

@app.post(
    "/groups",
    summary="Create New Tab Group",
    tags=["Group"],
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TabGroupRead
)
def create_group(
    payload: schemas.TabGroupCreate,
    db: Session = Depends(get_db)
):
    new_group = TabGroup(**payload.model_dump())
    db.add(new_group)
    db.commit()
    db.refresh(new_group) # we want to pull the newly generated id/updated_at
    return new_group

@app.patch(
    "/groups/{id}",
    summary="Update Tab Group",
    tags=["Group"],
    response_model=schemas.TabGroupRead
)
def update_group(
    id: uuid.UUID,
    payload: schemas.TabGroupUpdate,
    db: Session = Depends(get_db)
):
    group = db.get(TabGroup, id)
    if not group:
        raise HTTPException(status_code=404, detail="Tab group not found")
    
    update_data = payload.model_dump(exclude_unset=True) # we only want the fields that the user has actually changed

    for key, value in update_data.items():
        setattr(group, key, value)

    db.commit()
    db.refresh(group)
    return group

@app.delete(
    "/groups/{id}",
    summary="Delete Tab Group",
    tags=["Group"],
    response_model=schemas.TabGroupRead
)
def delete_group(
    id: uuid.UUID,
    db: Session = Depends(get_db)
):
    group = db.get(TabGroup, id)

    if not group:
        raise HTTPException(status_code=404, detail="Tab group not found")

    if group.deleted:
        raise HTTPException(status_code=412, detail="Tab group already deleted")

    group.deleted = True

    db.commit()
    db.refresh(group)

    return group

@app.get(
    "/health",
    summary="Health Check",
    tags=["System"]
)
def health_check():
    return {"message": "ok"}