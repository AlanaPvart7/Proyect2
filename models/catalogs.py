from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import re

class Catalog(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB, no es necesario enviarlo en POST",
        example="507f1f77bcf86cd799439011"
    )

    id_catalog_type: str = Field(
        description="ID del tipo de catálogo al que pertenece",
        examples=["507f1f77bcf86cd799439011"]
    )

    id_artist: Optional[str] = Field(
        default=None,
        description="ID del artista asociado (opcional)",
        examples=["507f1f77bcf86cd799439022"]
    )

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Nombre del catálogo",
        examples=["Blonde – Frank Ocean (Vinilo)", "In Rainbows – Radiohead (Vinilo)"]
    )

    description: str = Field(
        min_length=1,
        max_length=500,
        description="Descripción detallada del catálogo",
        examples=["Álbum de R&B alternativo por Frank Ocean"]
    )

    cost: float = Field(
        gt=0,
        description="Costo del catálogo",
        examples=[69.99, 79.99]
    )

    discount: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Descuento en porcentaje (0-100)",
        examples=[0, 10, 15]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del catálogo"
    )
