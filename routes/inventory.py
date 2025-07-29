from fastapi import APIRouter, Depends, Query
from fastapi import Request
from models.inventory import InventoryItem, CreateInventory, UpdateInventory
from controllers.inventory import (
    create_inventory_controller,
    get_inventory_controller,
    get_inventory_by_id_controller,
    update_inventory_controller
)
from utils.security import validate_admin  # función que usa Depends

router = APIRouter(prefix="/inventory", tags=["📝Inventory"])


@router.get("/", response_model=list[InventoryItem])
async def get_all_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(0, ge=0),  # 0 = sin límite
    available_only: bool = Query(False),
    admin_data: dict = Depends(validate_admin)
):
    actual_limit = limit if limit > 0 else None
    return await get_inventory_controller(skip=skip, limit=actual_limit, available_only=available_only)



@router.get("/{item_id}", response_model=InventoryItem)
async def get_inventory_by_id(
    item_id: str,
    admin_data: dict = Depends(validate_admin)
):
    return await get_inventory_by_id_controller(item_id)


@router.post("/", response_model=InventoryItem)
async def create_inventory(
    item: CreateInventory,
    admin_data: dict = Depends(validate_admin)
):
    return await create_inventory_controller(item)


@router.put("/{item_id}", response_model=InventoryItem)
async def update_inventory(
    item_id: str,
    item: UpdateInventory,
    admin_data: dict = Depends(validate_admin)
):
    return await update_inventory_controller(item_id, item)
