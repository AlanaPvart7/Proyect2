from bson import ObjectId

def get_order_details_pipeline(order_id: str) -> list:
    """Pipeline para obtener todos los detalles activos de una orden con info del inventario (producto)."""
    if not ObjectId.is_valid(order_id):
        raise ValueError(f"ID de orden no válido: {order_id}")
    
    return [
        {"$match": {"id_order": order_id, "active": True}},  # id_order es string en docs order_details, no ObjectId
        {
            "$lookup": {
                "from": "inventory",
                "localField": "id_inventory",
                "foreignField": "_id",
                "as": "product_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_order": 1,
                "id_inventory": {"$toString": "$id_inventory"},
                "product_name": {"$arrayElemAt": ["$product_info.name", 0]},
                "product_cost": {"$arrayElemAt": ["$product_info.cost", 0]},
                "quantity": 1,
                "active": 1,
                "date_created": 1,
                "date_updated": 1,
                "_id": 0
            }
        },
        {"$sort": {"date_created": 1}}
    ]

def validate_order_exists_pipeline(order_id: str) -> list:
    if not ObjectId.is_valid(order_id):
        raise ValueError(f"ID de orden no válido: {order_id}")

    return [
        {"$match": {"_id": ObjectId(order_id)}},
        {"$limit": 1}
    ]

def validate_product_exists_pipeline(product_id: str) -> list:
    if not ObjectId.is_valid(product_id):
        raise ValueError(f"ID de producto no válido: {product_id}")

    return [
        {"$match": {"_id": ObjectId(product_id)}},
        {"$limit": 1}
    ]

def check_order_detail_exists_pipeline(order_id: str, product_id: str) -> list:
    if not ObjectId.is_valid(product_id):
        raise ValueError(f"ID de producto no válido: {product_id}")

    return [
        {
            "$match": {
                "id_order": order_id,  # id_order es string en order_details
                "id_inventory": product_id,  # id_inventory es string en order_details
                "active": True
            }
        },
        {"$limit": 1}
    ]

def get_order_detail_by_id_pipeline(detail_id: str) -> list:
    if not ObjectId.is_valid(detail_id):
        raise ValueError(f"ID de detalle no válido: {detail_id}")

    return [
        {"$match": {"_id": ObjectId(detail_id)}},
        {
            "$lookup": {
                "from": "inventory",
                "localField": "id_inventory",
                "foreignField": "_id",
                "as": "product_info"
            }
        },
        {
            "$lookup": {
                "from": "orders",
                "localField": "id_order",
                "foreignField": "_id",
                "as": "order_info"
            }
        },
        {
            "$project": {
                "_id": 1,
                "id_order": 1,
                "id_inventory": 1,
                "quantity": 1,
                "active": 1,
                "product_info": {"$arrayElemAt": ["$product_info", 0]},
                "order_info": {"$arrayElemAt": ["$order_info", 0]}
            }
        }
    ]

