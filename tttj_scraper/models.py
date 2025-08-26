from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Reviewer(BaseModel):
    display_name: Optional[str] = None
    profile_url: Optional[HttpUrl] = None
    contributions_count: Optional[int] = None
    location: Optional[str] = None


class OwnerResponse(BaseModel):
    date: Optional[str] = None
    text: Optional[str] = None


class Review(BaseModel):
    rating: Optional[float] = None
    date: Optional[str] = None
    text: Optional[str] = None
    photos_count: Optional[int] = Field(None, description="Number of photos attached")
    likes_count: Optional[int] = None
    reviewer: Optional[Reviewer] = None
    owner_response: Optional[OwnerResponse] = None


class PlaceInfo(BaseModel):
    name: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    plus_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PlaceResult(BaseModel):
    place: PlaceInfo
    reviews: List[Review] = Field(default_factory=list)



