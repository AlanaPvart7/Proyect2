from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID de la reseña"
    )

    id_user: str = Field(
        description="ID del usuario que hizo la reseña",
        examples=["64d123abc45f6789e0a1b2c3"]
    )

    id_catalog: str = Field(
        description="ID del catálogo/producto reseñado",
        examples=["64d987xyz12k3456q7w8e9r0"]
    )

    comment: str = Field(
        description="Opinión escrita por el usuario",
        min_length=1,
        max_length=1000,
        examples=["Me encanta este álbum"]
    )

    rating: int = Field(
        description="Calificación de 1 a 5 estrellas",
        ge=1,
        le=5,
        examples=[5]
    )

    review_date: Optional[datetime] = Field(
        default=None,
        description="Fecha en que se hizo la reseña"
    )

    active: bool = Field(
        default=True,
        description="Indica si la reseña está activa o eliminada (soft delete)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_user": "64d123abc45f6789e0a1b2c3",
                "id_catalog": "64d987xyz12k3456q7w8e9r0",
                "comment": "Me encantó este disco",
                "rating": 5,
                "review_date": "2024-01-15",
                "active": True
    }
}