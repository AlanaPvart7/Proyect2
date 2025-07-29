from pydantic import BaseModel, Field
from typing import Optional

class Artist(BaseModel):
    id: Optional[str] = Field(
        default=None, 
        description="MongoDB ID del artista"
        )

    artist_name: str = Field(
        description="Nombre del artista",
        min_length=1,
        max_length=100,
        examples=["Frank Ocean", "Radiohead"]
    )

    activity_year: int = Field(
        description="Año en que el artista comenzó su actividad",
        ge=1900,
        le=2100,
        examples=[1982, 2010, 2015]
    )

    music_genre: str = Field(
        description="Género musical del artista",
        min_length=2,
        max_length=100,
        examples=["R&B / Neo Soul", "Experimental / Art Rock", "Alternative Rock"]
    )

    active: bool = Field(
        default=True, 
        description="Indica si el artista está activo (soft delete)"
        )
