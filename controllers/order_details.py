from datetime import datetime
from bson import ObjectId
from models.order_details import CreateOrderDetail, UpdateOrderDetail
from pipelines.order_detail_pipelines import get_order_details_pipeline
from utils.mongodb import get_collection

# Conexión a las colecciones
order_details_collection = get_collection("order_details")
orders_collection = get_collection("orders")
catalogs_collection = get_collection("catalogs")

# Funciones helper
async def recalculate_order_totals(order_id: str) -> dict:
    """Recalcular y actualizar los totales de una orden basado en sus detalles activos."""
    try:
        pipeline = [
            {"$match": {"id_order": order_id, "active": True}},
            {
                "$lookup": {
                    "from": "catalogs",
                    "let": {"product_id": {"$toObjectId": "$id_producto"}},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$product_id"]}}}],
                    "as": "product_info"
                }
            },
            {"$addFields": {
                "product_price": {"$arrayElemAt": ["$product_info.cost", 0]},
                "line_subtotal": {
                    "$cond": {
                        "if": {"$gt": [{"$size": "$product_info"}, 0]},
                        "then": {"$multiply": ["$quantity", {"$arrayElemAt": ["$product_info.cost", 0]}]},
                        "else": 0
                    }
                }
            }},
            {"$group": {
                "_id": None,
                "subtotal": {"$sum": "$line_subtotal"},
                "total_items": {"$sum": "$quantity"}
            }}
        ]
        
        # Ejecutar pipeline para calcular subtotales
        result = list(order_details_collection.aggregate(pipeline))

        if result and result[0]["subtotal"] > 0:
            subtotal = result[0]["subtotal"]
            tax_rate = 0.15  # Tasa de impuestos
            taxes = subtotal * tax_rate
            discount = 0.0  # Si tuvieras lógica de descuentos, agregalo aquí
            total = subtotal + taxes - discount

            update_result = orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "subtotal": round(subtotal, 2),
                        "taxes": round(taxes, 2),
                        "discount": discount,
                        "total": round(total, 2),
                        "date_updated": datetime.utcnow()
                    }
                }
            )

            if update_result.modified_count > 0:
                return {
                    "success": True,
                    "subtotal": round(subtotal, 2),
                    "taxes": round(taxes, 2),
                    "discount": discount,
                    "total": round(total, 2)
                }
        else:
            # Si no hay productos, resetear totales a cero
            orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "subtotal": 0.0,
                        "taxes": 0.0,
                        "discount": 0.0,
                        "total": 0.0,
                        "date_updated": datetime.utcnow()
                    }
                }
            )
            return {"success": True, "subtotal": 0.0, "taxes": 0.0, "discount": 0.0, "total": 0.0}
    except Exception as e:
        return {"success": False, "message": str(e)}

# Funciones CRUD
async def create_order_detail(order_id: str, detail_data: CreateOrderDetail, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    """Crear un nuevo detalle de orden"""
    try:
        if not ObjectId.is_valid(order_id):
            return {"success": False, "message": "ID de orden inválido", "data": None}

        # Verificar existencia de la orden
        order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order_info:
            return {"success": False, "message": "Orden no encontrada", "data": None}

        if not is_admin and requesting_user_id:
            if order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para modificar esta orden", "data": None}

        # Verificar existencia del producto
        product_exists = catalogs_collection.find_one({"_id": ObjectId(detail_data.id_producto)})
        if not product_exists:
            return {"success": False, "message": "Producto no encontrado", "data": None}

        # Verificar si el producto ya está en la orden
        existing_detail = order_details_collection.find_one({
            "id_order": order_id, "id_producto": detail_data.id_producto, "active": True
        })

        if existing_detail:
            return {"success": False, "message": "Este producto ya está en la orden", "data": None}

        # Crear detalle de orden
        detail_dict = detail_data.dict()
        detail_dict["id_order"] = order_id
        detail_dict["date_created"] = datetime.utcnow()
        detail_dict["date_updated"] = datetime.utcnow()
        detail_dict["active"] = True

        result = order_details_collection.insert_one(detail_dict)
        
        if result.inserted_id:
            # Recalcular totales de la orden
            totals_result = await recalculate_order_totals(order_id)
            
            response_data = {"id": str(result.inserted_id)}
            if totals_result["success"]:
                response_data["order_totals"] = {
                    "subtotal": totals_result["subtotal"],
                    "taxes": totals_result["taxes"],
                    "discount": totals_result["discount"],
                    "total": totals_result["total"]
                }
            
            return {"success": True, "message": "Producto agregado a la orden", "data": response_data}
        
        return {"success": False, "message": "Error al agregar el producto", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

# Funciones de consulta
async def get_order_details(order_id: str, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    """Obtener detalles de una orden específica"""
    try:
        if not ObjectId.is_valid(order_id):
            return {"success": False, "message": "ID de orden inválido", "data": None}

        order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order_info:
            return {"success": False, "message": "Orden no encontrada", "data": None}

        if not is_admin and requesting_user_id:
            if order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para ver esta orden", "data": None}

        pipeline = get_order_details_pipeline(order_id)
        details = list(order_details_collection.aggregate(pipeline))

        return {"success": True, "message": "Detalles obtenidos exitosamente", "data": {"order_id": order_id, "details": details}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

# Funciones de actualización
async def update_order_detail(order_id: str, detail_id: str, update_data: UpdateOrderDetail, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    """Actualizar un detalle de orden"""
    try:
        if not ObjectId.is_valid(order_id) or not ObjectId.is_valid(detail_id):
            return {"success": False, "message": "ID inválido", "data": None}

        detail_info = order_details_collection.find_one({
            "_id": ObjectId(detail_id), "id_order": order_id, "active": True
        })

        if not detail_info:
            return {"success": False, "message": "Detalle no encontrado o no pertenece a esta orden", "data": None}

        if not is_admin and requesting_user_id:
            order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
            if order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para modificar este detalle", "data": None}

        update_dict = update_data.dict()
        update_dict["date_updated"] = datetime.utcnow()

        result = order_details_collection.update_one({"_id": ObjectId(detail_id)}, {"$set": update_dict})

        if result.modified_count > 0:
            totals_result = await recalculate_order_totals(order_id)
            return {"success": True, "message": "Detalle actualizado exitosamente", "data": totals_result}
        return {"success": False, "message": "No se pudo actualizar el detalle", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

# Funciones de eliminación
async def delete_order_detail(order_id: str, detail_id: str, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    """Eliminar un detalle de orden"""
    try:
        if not ObjectId.is_valid(order_id) or not ObjectId.is_valid(detail_id):
            return {"success": False, "message": "ID inválido", "data": None}

        detail_info = order_details_collection.find_one({
            "_id": ObjectId(detail_id), "id_order": order_id, "active": True
        })

        if not detail_info:
            return {"success": False, "message": "Detalle no encontrado o no pertenece a esta orden", "data": None}

        if not is_admin and requesting_user_id:
            order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
            if order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para eliminar este detalle", "data": None}

        result = order_details_collection.update_one(
            {"_id": ObjectId(detail_id)}, {"$set": {"active": False, "date_updated": datetime.utcnow()}}
        )

        if result.modified_count > 0:
            totals_result = await recalculate_order_totals(order_id)
            return {"success": True, "message": "Detalle eliminado exitosamente", "data": totals_result}

        return {"success": False, "message": "No se pudo eliminar el detalle", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
