from typing import Optional, List

from pydantic import BaseModel, Field


class TripRequirements(BaseModel):

    origin: str

    destination: str

    start_date: Optional[str] = None

    end_date: Optional[str] = None

    days: int = Field(
        ...,
        ge=1,
        le=30
    )

    travelers: int = Field(
        1,
        ge=1
    )

    budget: Optional[float] = Field(
        None,
        ge=0
    )

    currency: str = "INR"

    transport_type: Optional[str] = None

    interests: List[str] = Field(
        default_factory=list
    )

    hotel_preference: Optional[str] = None