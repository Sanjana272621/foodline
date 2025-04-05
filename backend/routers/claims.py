from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import get_db
from routers.users import get_current_user

router = APIRouter(
    prefix="/claims",
    tags=["claims"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.ClaimResponse)
def create_claim(
    claim: schemas.ClaimCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "recipient":
        raise HTTPException(
            status_code=403, 
            detail="Only recipients can claim gatherings"
        )
    
    result = crud.create_claim(db=db, claim=claim, recipient_id=current_user.id)
    if not result:
        raise HTTPException(
            status_code=400, 
            detail="Gathering not found or already claimed"
        )
    return result

@router.put("/{claim_id}/status", response_model=schemas.ClaimResponse)
def update_claim_status(
    claim_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Validate status
    if status not in ["claimed", "collected", "cancelled"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid status. Must be 'claimed', 'collected', or 'cancelled'"
        )
    
    # Get claim to check ownership
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Check if user is authorized to update this claim
    gathering = crud.get_gathering(db, gathering_id=claim.gathering_id)
    
    if (current_user.user_type == "recipient" and claim.recipient_id != current_user.id) or \
       (current_user.user_type == "donor" and gathering.user_id != current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to update this claim"
        )
    
    # Update status
    updated_claim = crud.update_claim_status(db, claim_id=claim_id, status=status)
    if not updated_claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return updated_claim

@router.get("/my-claims", response_model=List[schemas.ClaimDetail])
def read_user_claims(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "recipient":
        raise HTTPException(
            status_code=403, 
            detail="Only recipients can view their claims"
        )
    claims = crud.get_user_claims(db, user_id=current_user.id)
    return claims

@router.get("/for-my-gatherings", response_model=List[schemas.ClaimDetail])
def read_claims_for_user_gatherings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.user_type != "donor":
        raise HTTPException(
            status_code=403, 
            detail="Only donors can view claims for their gatherings"
        )
    
    # Get all user's gatherings
    gatherings = crud.get_user_gatherings(db, user_id=current_user.id)
    gathering_ids = [g.id for g in gatherings]
    
    # Get all claims for these gatherings
    claims = db.query(models.Claim).filter(models.Claim.gathering_id.in_(gathering_ids)).all()
    return claims