from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class Catalog(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID"
    )

    id_catalog_type: str = Field(
        description="ID del tipo de catálogo al que pertenece",
        examples=["507f1f77bcf86cd799439011"]
    )

    name: str = Field(
        description="Nombre del catálogo",
        min_length=1,
        max_length=100,
        examples=["Akrilla Album Epistolares", "Frank Ocean Vinilo - Blonde"]
    )

    description: str = Field(
        description="Descripción detallada del catálogo",
        min_length=1,
        max_length=500,
        examples=["Album de estudio de Akrilla con letras profundas y emotivas.", "Vinilo de colección de Frank Ocean con sonido excepcional."]
    )

    cost: float = Field(
        description="Costo del producto",
        gt=0,
        examples=[15000.50000, 549.99]
    )

    discount: int = Field(
        description="Descuento en porcentaje (0-100)",
        ge=0,
        le=100,
        default=0,
        examples=[10, 25, 0]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del catálogo"
    )