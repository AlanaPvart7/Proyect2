from fastapi import APIRouter, HTTPException, Request
from models.order_statuses import OrderStatus
from controllers.order_statuses import (
    create_order_status,
    get_order_statuses,
    get_order_status_by_id,
    update_order_status,
    delete_order_status
)
from utils.security import validateadmin

router = APIRouter(prefix="/order-statuses", tags=["📊 Order Status"])

@router.post("/", response_model=dict)
@validateadmin
async def create_order_status_endpoint(
    order_status: OrderStatus, request: Request) -> dict:
    """Crear un nuevo order status (requiere permisos de admin)"""
    return await create_order_status(order_status)

@router.get("/")
async def get_order_statuses_endpoint() -> dict:
    """Obtener todos los order statuses"""
    return await get_order_statuses()

@router.get("/{order_status_id}")
async def get_order_status_by_id_endpoint(order_status_id: str) -> dict:
    """Obtener un order status por ID"""
    return await get_order_status_by_id(order_status_id)

@router.put("/{order_status_id}")
@validateadmin
async def update_order_status_endpoint(order_status_id: str, order_status: OrderStatus, request: Request) -> dict:
    """Actualizar un order status (requiere permisos de admin)"""
    return await update_order_status(order_status_id, order_status)

@router.delete("/{order_status_id}")
@validateadmin
async def delete_order_status_endpoint( order_status_id: str, request: Request ) -> dict:
    """Eliminar un order status (requiere permisos de admin)"""
    return await delete_order_status(order_status_id)