from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    user_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in ["donor", "recipient"]:
            raise ValueError('user_type must be either "donor" or "recipient"')
        return v

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# Gathering schemas
class GatheringBase(BaseModel):
    food_details: str
    available_from: datetime
    available_to: datetime
    latitude: float
    longitude: float

class GatheringCreate(GatheringBase):
    pass

class GatheringResponse(GatheringBase):
    id: int
    user_id: int
    is_taken: bool
    
    class Config:
        orm_mode = True

class GatheringDetail(GatheringResponse):
    user: UserResponse
    
    class Config:
        orm_mode = True

# Claim schemas
class ClaimBase(BaseModel):
    gathering_id: int

class ClaimCreate(ClaimBase):
    pass

class ClaimResponse(ClaimBase):
    id: int
    recipient_id: int
    claim_time: datetime
    status: str
    
    class Config:
        orm_mode = True

class ClaimDetail(ClaimResponse):
    gathering: GatheringResponse
    recipient: UserResponse
    
    class Config:
        orm_mode = True