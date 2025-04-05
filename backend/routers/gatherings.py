from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import crud, models, schemas
from database import get_db
from routers.users import get_current_user

router = APIRouter(
    prefix="/gatherings",
    tags=["gatherings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.GatheringResponse)
def create_gathering(
    gathering: schemas.GatheringCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "donor":
        raise HTTPException(
            status_code=403, 
            detail="Only donors can create gatherings"
        )
    return crud.create_gathering(db=db, gathering=gathering, user_id=current_user.id)

@router.get("/", response_model=List[schemas.GatheringResponse])
def read_gatherings(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "recipient":
        raise HTTPException(
            status_code=403, 
            detail="Only recipients can view available gatherings"
        )
    gatherings = crud.get_available_gatherings(db, skip=skip, limit=limit)
    return gatherings

@router.get("/nearby", response_model=List[schemas.GatheringResponse])
def read_nearby_gatherings(
    latitude: float = Query(...),
    longitude: float = Query(...),
    max_distance: float = Query(10.0),  # Default 10 km
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "recipient":
        raise HTTPException(
            status_code=403, 
            detail="Only recipients can view nearby gatherings"
        )
    gatherings = crud.get_nearby_gatherings(
        db, 
        latitude=latitude, 
        longitude=longitude, 
        max_distance_km=max_distance
    )
    return gatherings

@router.get("/my-donations", response_model=List[schemas.GatheringResponse])
def read_user_gatherings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "donor":
        raise HTTPException(
            status_code=403, 
            detail="Only donors can view their donations"
        )
    gatherings = crud.get_user_gatherings(db, user_id=current_user.id)
    return gatherings

@router.get("/{gathering_id}", response_model=schemas.GatheringDetail)
def read_gathering(
    gathering_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    gathering = crud.get_gathering(db, gathering_id=gathering_id)
    if gathering is None:
        raise HTTPException(status_code=404, detail="Gathering not found")
    
    # Donors can only see their own gatherings
    if current_user.user_type == "donor" and gathering.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Access denied"
        )
    
    # Recipients can only see available gatherings
    if current_user.user_type == "recipient" and gathering.is_taken:
        # Unless they claimed it themselves
        claim = db.query(models.Claim).filter(
            models.Claim.gathering_id == gathering_id,
            models.Claim.recipient_id == current_user.id
        ).first()
        
        if not claim:
            raise HTTPException(
                status_code=403, 
                detail="This gathering is no longer available"
            )
            
    return gathering