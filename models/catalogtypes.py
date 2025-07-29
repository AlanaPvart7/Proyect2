from pydantic import BaseModel, Field
from typing import Optional

class CatalogType(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="ID autogenerado por MongoDB",
        example="64b8d9ecf0c5eaa5e2a04f87"
    )
    description: str = Field(
        description="Descripción del tipo de catálogo (Vinilo, CD, etc.)",
        example="Vinilo"
    )
    active: Optional[bool] = Field(
        default=True,
        description="Estado activo del tipo de catálogo",
        example=True
    )
