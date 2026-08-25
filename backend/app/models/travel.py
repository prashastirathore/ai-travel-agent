from typing import List, Optional

from pydantic import BaseModel, Field


class TravelRequest(BaseModel):

    origin: str = Field(
        ...,
        description="Starting city or airport"
    )

    destination: str = Field(
        ...,
        description="Destination city or airport"
    )

    departure_date: str = Field(
        ...,
        description="Departure date YYYY-MM-DD"
    )

    return_date: str = Field(
        ...,
        description="Return date YYYY-MM-DD"
    )

    days: int = Field(
        ...,
        ge=1,
        le=30
    )

    budget: Optional[float] = Field(
        None,
        ge=0
    )

    travelers: int = Field(
        1,
        ge=1
    )

    preferences: List[str] = Field(
        default_factory=list
    )