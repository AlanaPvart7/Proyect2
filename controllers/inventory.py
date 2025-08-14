from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from utils.mongodb import get_collection
from models.inventory import InventoryItem, CreateInventory, UpdateInventory
from pipelines.inventory_pipelines import (
    get_all_inventory_pipeline,
    get_inventory_by_id_pipeline,
    validate_catalog_pipeline,
    get_inventory_pipeline
)
from anyio.to_thread import run_sync  # importante para ejecutar código bloqueante sin bloquear el event loop

coll = get_collection("inventory")
catalog_coll = get_collection("catalogs")  # colección de catálogos


async def create_inventory_controller(item: CreateInventory) -> dict:
    try:
        item_dict = item.dict()

        # Conversión obligatoria: date → datetime
        item_dict["entry_date"] = datetime.combine(item_dict["entry_date"], datetime.min.time())

        item_dict["active"] = True
        result = coll.insert_one(item_dict)
        item_dict["id"] = str(result.inserted_id)
        return item_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando inventario: {str(e)}")



async def get_inventory_controller(skip: int = 0, limit: int = 0, available_only: bool = False) -> list[InventoryItem]:
    try:
        pipeline = get_inventory_pipeline(skip=skip, limit=limit, available_only=available_only)
        results = await run_sync(lambda: list(coll.aggregate(pipeline)))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo inventario: {str(e)}")


async def get_inventory_by_id_controller(item_id: str) -> InventoryItem:
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        pipeline = get_inventory_by_id_pipeline(item_id)
        results = await run_sync(lambda: list(coll.aggregate(pipeline)))
        if not results:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")

        return InventoryItem(**results[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando inventario: {str(e)}")


async def update_inventory_controller(item_id: str, item: UpdateInventory) -> InventoryItem:
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        update_data = item.model_dump(exclude_unset=True)

        result = await run_sync(
            lambda: coll.update_one(
                {"_id": ObjectId(item_id), "active": True},
                {"$set": update_data}
            )
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")

        return await get_inventory_by_id_controller(item_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando inventario: {str(e)}")
