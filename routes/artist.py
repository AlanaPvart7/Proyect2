from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from models.artist import Artist
from controllers import artist as artist_controller

router = APIRouter(prefix="/artists", tags=["🎤 Artists"])

# Validación de header admin como dependencia
async def validateadmin(admin: Optional[str] = Header(None)):
    if admin != "true":
        raise HTTPException(status_code=403, detail="Admin header required")

# GET /artists - listar todos los artistas
@router.get("/", summary="Listar todos los artistas", response_model=list[Artist])
async def get_all_artists():
    return await artist_controller.get_artists()

# GET /artists/{id} - obtener artista por ID
@router.get("/{artist_id}", summary="Obtener artista por ID", response_model=Artist)
async def get_artist_by_id(artist_id: str):
    return await artist_controller.get_artist_by_id(artist_id)

# POST /artists - crear artista (admin)
@router.post("/", summary="Crear artista", response_model=Artist, dependencies=[Depends(validateadmin)])
async def create_artist(artist: Artist):
    return await artist_controller.create_artist(artist)

# PUT /artists/{id} - actualizar artista (admin)
@router.put("/{artist_id}", summary="Actualizar artista", response_model=Artist, dependencies=[Depends(validateadmin)])
async def update_artist(artist_id: str, artist: Artist):
    return await artist_controller.update_artist(artist_id, artist)

# DELETE /artists/{id} - desactivar artista (admin)
@router.delete("/{artist_id}", summary="Eliminar artista", response_model=Artist, dependencies=[Depends(validateadmin)])
async def delete_artist(artist_id: str):
    return await artist_controller.delete_artist(artist_id)
