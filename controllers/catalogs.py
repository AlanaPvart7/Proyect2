from models.catalogs import Catalog
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId, errors
from pipelines.catalog_pipelines import (
    search_catalogs_pipeline,
    validate_catalog_type_pipeline,
    get_catalog_with_type_pipeline,
    get_catalogs_by_type_pipeline,
    get_all_catalogs_with_types_pipeline
)

coll = get_collection("catalogs")
catalog_types_coll = get_collection("catalogtypes")


async def create_catalog(catalog: Catalog, user: dict) -> Catalog:
    try:
        try:
            catalog_type_oid = ObjectId(catalog.id_catalog_type)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid catalog type ID format")

        pipeline = validate_catalog_type_pipeline(catalog.id_catalog_type)
        catalog_type_result = list(catalog_types_coll.aggregate(pipeline))
        if not catalog_type_result:
            raise HTTPException(status_code=400, detail="Catalog type not found or inactive")

        catalog.name = catalog.name.strip()
        catalog.description = catalog.description.strip()

        existing = coll.find_one({"name": {"$regex": f"^{catalog.name}$", "$options": "i"}})
        if existing:
            raise HTTPException(status_code=400, detail="Catalog with this name already exists")

        catalog_dict = catalog.model_dump(exclude={"id"})
        inserted = coll.insert_one(catalog_dict)
        catalog.id = str(inserted.inserted_id)
        return catalog

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating catalog: {str(e)}")


async def get_catalogs(skip: int = 0, limit: int = 10) -> dict:
    try:
        pipeline = get_all_catalogs_with_types_pipeline(skip, limit)
        catalogs_raw = list(coll.aggregate(pipeline))

        total_count = coll.count_documents({"active": True})

        return {
            "catalogs": catalogs_raw,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching catalogs: {str(e)}")


async def get_catalog_by_id(catalog_id: str) -> dict:
    try:
        try:
            _ = ObjectId(catalog_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid catalog ID format")

        pipeline = get_catalog_with_type_pipeline(catalog_id)
        result = list(coll.aggregate(pipeline))
        if not result:
            raise HTTPException(status_code=404, detail="Catalog not found")

        return result[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching catalog: {str(e)}")


async def get_catalogs_by_type(catalog_type_description: str, skip: int = 0, limit: int = 10) -> dict:
    try:
        pipeline = get_catalogs_by_type_pipeline(catalog_type_description, skip, limit)
        catalogs_raw = list(coll.aggregate(pipeline))

        count_pipeline = [
            {"$lookup": {
                "from": "catalogtypes",
                "localField": "id_catalog_type",
                "foreignField": "_id",
                "as": "catalog_type"
            }},
            {"$unwind": "$catalog_type"},
            {"$match": {
                "catalog_type.description": {"$regex": f"^{catalog_type_description}$", "$options": "i"},
                "active": True
            }},
            {"$count": "total"}
        ]
        count_result = list(coll.aggregate(count_pipeline))
        total_count = count_result[0]["total"] if count_result else 0

        return {
            "catalogs": catalogs_raw,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "catalog_type": catalog_type_description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching catalogs by type: {str(e)}")


async def update_catalog(catalog_id: str, catalog: Catalog, user: dict) -> dict:
    try:
        try:
            catalog_oid = ObjectId(catalog_id)
            catalog_type_oid = ObjectId(catalog.id_catalog_type)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ID format")

        # Validar existencia y estado activo del tipo catálogo con pipeline
        pipeline = validate_catalog_type_pipeline(catalog.id_catalog_type)
        catalog_type_result = list(catalog_types_coll.aggregate(pipeline))
        if not catalog_type_result:
            raise HTTPException(status_code=400, detail="Catalog type not found or inactive")

        catalog.name = catalog.name.strip()
        catalog.description = catalog.description.strip()

        existing = coll.find_one({
            "name": {"$regex": f"^{catalog.name}$", "$options": "i"},
            "_id": {"$ne": catalog_oid}
        })
        if existing:
            raise HTTPException(status_code=400, detail="Catalog with this name already exists")

        update_data = catalog.model_dump(exclude={"id"})
        result = coll.update_one({"_id": catalog_oid}, {"$set": update_data})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Catalog not found")

        return await get_catalog_by_id(catalog_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating catalog: {str(e)}")


async def deactivate_catalog(catalog_id: str, user: dict) -> dict:
    try:
        try:
            catalog_oid = ObjectId(catalog_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid catalog ID format")

        result = coll.update_one({"_id": catalog_oid}, {"$set": {"active": False}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Catalog not found")

        # desactivar 
        inventory_coll = get_collection("inventory")
        await inventory_coll.update_many({"catalog_id": catalog_oid}, {"$set": {"active": False}})

        return await get_catalog_by_id(catalog_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating catalog: {str(e)}")



async def search_catalogs(q: str, skip: int = 0, limit: int = 10) -> dict:
    try:
        pipeline = search_catalogs_pipeline(q, skip, limit)
        results = list(coll.aggregate(pipeline))

        total_count = coll.count_documents({
            "active": True,
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]
        })

        return {
            "catalogs": results,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching catalogs: {str(e)}")
