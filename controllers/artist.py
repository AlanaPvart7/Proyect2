from fastapi import HTTPException
from bson import ObjectId
from utils.mongodb import get_collection
from models.artist import Artist

coll = get_collection("artists")

async def create_artist(artist: Artist) -> Artist:
    try:
        artist_dict = artist.model_dump(exclude={"id"})
        result = coll.insert_one(artist_dict)
        artist.id = str(result.inserted_id)
        return artist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando artista: {str(e)}")

async def get_artists() -> list[Artist]:
    try:
        artists = []
        for doc in coll.find({"active": True}):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            artists.append(Artist(**doc))
        return artists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo artistas: {str(e)}")

async def get_artist_by_id(artist_id: str) -> Artist:
    try:
        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="ID de artista inválido")
        doc = coll.find_one({"_id": ObjectId(artist_id), "active": True})
        if not doc:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Artist(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo artista: {str(e)}")

async def update_artist(artist_id: str, artist: Artist) -> Artist:
    try:
        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="ID de artista inválido")
        update_data = artist.model_dump(exclude={"id"})
        result = coll.update_one({"_id": ObjectId(artist_id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        return await get_artist_by_id(artist_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando artista: {str(e)}")

async def delete_artist(artist_id: str) -> Artist:
    try:
        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="ID de artista inválido")
        result = coll.update_one({"_id": ObjectId(artist_id)}, {"$set": {"active": False}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        return await get_artist_by_id(artist_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando artista: {str(e)}")
