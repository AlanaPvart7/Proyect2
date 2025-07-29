from models.catalogtypes import CatalogType
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId, errors

coll = get_collection("catalogtypes")

async def create_catalog_type(catalog_type: CatalogType) -> CatalogType:
    try:
        # Solo limpiamos espacios
        catalog_type.description = catalog_type.description.strip()

        # Verificación de duplicado insensible a mayúsculas
        existing = coll.find_one({
            "description": {"$regex": f"^{catalog_type.description}$", "$options": "i"},
            "active": True
        })
        if existing:
            raise HTTPException(status_code=400, detail="Catalog type already exists")

        catalog_type_dict = catalog_type.model_dump(exclude={"id"})
        inserted = coll.insert_one(catalog_type_dict)
        catalog_type.id = str(inserted.inserted_id)
        return catalog_type
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating catalog type: {str(e)}")

async def get_catalog_types() -> list[CatalogType]:
    try:
        catalog_types = []
        for doc in coll.find({"active": True}):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            catalog_types.append(CatalogType(**doc))
        return catalog_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching catalog types: {str(e)}")

async def get_catalog_type_by_id(catalog_type_id: str) -> CatalogType:
    try:
        try:
            oid = ObjectId(catalog_type_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ID format")

        doc = coll.find_one({"_id": oid, "active": True})
        if not doc:
            raise HTTPException(status_code=404, detail="Catalog type not found")
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return CatalogType(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching catalog type: {str(e)}")

async def update_catalog_type(catalog_type_id: str, catalog_type: CatalogType) -> CatalogType:
    try:
        try:
            oid = ObjectId(catalog_type_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ID format")

        catalog_type.description = catalog_type.description.strip().lower()

        existing = coll.find_one({
            "description": catalog_type.description,
            "_id": {"$ne": oid},
            "active": True
        })
        if existing:
            raise HTTPException(status_code=400, detail="Catalog type already exists")

        result = coll.update_one(
            {"_id": oid},
            {"$set": catalog_type.model_dump(exclude={"id"})}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Catalog type not found")

        return await get_catalog_type_by_id(catalog_type_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating catalog type: {str(e)}")

async def deactivate_catalog_type(catalog_type_id: str) -> CatalogType:
    try:
        try:
            oid = ObjectId(catalog_type_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ID format")

        result = coll.update_one({"_id": oid}, {"$set": {"active": False}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Catalog type not found")

        return await get_catalog_type_by_id(catalog_type_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating catalog type: {str(e)}")
    