from fastapi import APIRouter, HTTPException, Request
from models.order_details import CreateOrderDetail, UpdateOrderDetail
from controllers.order_details import (
    create_order_detail,
    update_order_detail,
    delete_order_detail,
    get_order_details
)
from utils.security import validateuser

router = APIRouter(prefix="/orders", tags=["🛒 Order Details"])

@router.post("/{order_id}/details")
@validateuser
async def add_product_to_order(
    request: Request,
    order_id: str,
    detail_data: CreateOrderDetail
):
    is_admin = getattr(request.state, 'admin', False)
    requesting_user_id = request.state.id if not is_admin else None

    result = await create_order_detail(order_id, detail_data, requesting_user_id, is_admin)

    if not result["success"]:
        if result["message"] == "Orden no encontrada":
            raise HTTPException(status_code=404, detail=result["message"])
        elif "permiso" in result["message"]:
            raise HTTPException(status_code=403, detail=result["message"])
        elif "ya está en la orden" in result["message"]:
            raise HTTPException(status_code=409, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.get("/{order_id}/details")
@validateuser
async def get_order_details_route(request: Request, order_id: str):
    is_admin = getattr(request.state, 'admin', False)
    requesting_user_id = request.state.id if not is_admin else None

    result = await get_order_details(order_id, requesting_user_id, is_admin)

    if not result["success"]:
        if result["message"] == "Orden no encontrada":
            raise HTTPException(status_code=404, detail=result["message"])
        elif "permiso" in result["message"]:
            raise HTTPException(status_code=403, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.put("/{order_id}/details/{detail_id}")
@validateuser
async def update_product_quantity(
    request: Request,
    order_id: str,
    detail_id: str,
    update_data: UpdateOrderDetail
):
    is_admin = getattr(request.state, 'admin', False)
    requesting_user_id = request.state.id if not is_admin else None

    result = await update_order_detail(order_id, detail_id, update_data, requesting_user_id, is_admin)

    if not result["success"]:
        if result["message"] == "Detalle no encontrado o no pertenece a esta orden":
            raise HTTPException(status_code=404, detail=result["message"])
        elif "permiso" in result["message"]:
            raise HTTPException(status_code=403, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.delete("/{order_id}/details/{detail_id}")
@validateuser
async def remove_product_from_order(
    request: Request,
    order_id: str,
    detail_id: str
):
    is_admin = getattr(request.state, 'admin', False)
    requesting_user_id = request.state.id if not is_admin else None

    result = await delete_order_detail(order_id, detail_id, requesting_user_id, is_admin)

    if not result["success"]:
        if result["message"] == "Detalle no encontrado o no pertenece a esta orden":
            raise HTTPException(status_code=404, detail=result["message"])
        elif "permiso" in result["message"]:
            raise HTTPException(status_code=403, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result
