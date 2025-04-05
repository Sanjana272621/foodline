from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from math import radians, cos, sin, asin, sqrt
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function to calculate distance between two lat/long points
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        user_type=user.user_type,
        latitude=user.latitude,
        longitude=user.longitude
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

# Gathering operations
def create_gathering(db: Session, gathering: schemas.GatheringCreate, user_id: int):
    db_gathering = models.Gathering(
        **gathering.dict(), 
        user_id=user_id, 
        is_taken=False
    )
    db.add(db_gathering)
    db.commit()
    db.refresh(db_gathering)
    return db_gathering

def get_gathering(db: Session, gathering_id: int):
    return db.query(models.Gathering).filter(models.Gathering.id == gathering_id).first()

def get_available_gatherings(db: Session, skip: int = 0, limit: int = 100):
    now = datetime.now()
    return db.query(models.Gathering).filter(
        and_(
            models.Gathering.is_taken == False,
            models.Gathering.available_from <= now,
            models.Gathering.available_to >= now
        )
    ).offset(skip).limit(limit).all()

def get_nearby_gatherings(db: Session, latitude: float, longitude: float, max_distance_km: float = 10):
    # Get all available gatherings
    now = datetime.now()
    gatherings = db.query(models.Gathering).filter(
        and_(
            models.Gathering.is_taken == False,
            models.Gathering.available_from <= now,
            models.Gathering.available_to >= now
        )
    ).all()
    
    # Filter gatherings by distance
    nearby_gatherings = []
    for gathering in gatherings:
        distance = haversine(latitude, longitude, gathering.latitude, gathering.longitude)
        if distance <= max_distance_km:
            gathering.distance = distance  # Add distance attribute
            nearby_gatherings.append(gathering)
    
    # Sort by distance
    nearby_gatherings.sort(key=lambda x: x.distance)
    return nearby_gatherings

# Claim operations
def create_claim(db: Session, claim: schemas.ClaimCreate, recipient_id: int):
    # Check if gathering exists and is not already taken
    gathering = get_gathering(db, claim.gathering_id)
    if not gathering:
        return None
    if gathering.is_taken:
        return None
    
    # Create claim and mark gathering as taken
    db_claim = models.Claim(
        gathering_id=claim.gathering_id,
        recipient_id=recipient_id,
        claim_time=datetime.now(),
        status="claimed"
    )
    
    gathering.is_taken = True
    
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

def update_claim_status(db: Session, claim_id: int, status: str):
    db_claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not db_claim:
        return None
    
    # If cancelling claim, mark gathering as available again
    if status == "cancelled" and db_claim.status != "cancelled":
        gathering = get_gathering(db, db_claim.gathering_id)
        gathering.is_taken = False
    
    db_claim.status = status
    db.commit()
    db.refresh(db_claim)
    return db_claim

def get_user_claims(db: Session, user_id: int):
    return db.query(models.Claim).filter(models.Claim.recipient_id == user_id).all()

def get_user_gatherings(db: Session, user_id: int):
    return db.query(models.Gathering).filter(models.Gathering.user_id == user_id).all()