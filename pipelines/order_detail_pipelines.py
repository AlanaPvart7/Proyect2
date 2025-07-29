from bson import ObjectId


def get_order_details_pipeline(order_id: str) -> list:
    """Pipeline para obtener TODOS los detalles de una orden con información del producto"""
    if not ObjectId.is_valid(order_id):
        raise ValueError(f"ID de orden no válido: {order_id}")
    
    return [
        {"$match": {"id_order": ObjectId(order_id), "active": True}},
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
                "id": {"$toString": "$_id"},  # Si es necesario convertir a string
                "id_order": {"$toString": "$id_order"},
                "id_inventory": {"$toString": "$id_inventory"},  # Verifica si es necesario
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
    """Pipeline para validar que una orden existe"""
    return [
        {"$match": {"_id": ObjectId(order_id)}},
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]


def validate_product_exists_pipeline(product_id: str) -> list:
    """Pipeline para validar que un producto existe"""
    return [
        {"$match": {"_id": ObjectId(product_id)}},
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]


def check_order_detail_exists_pipeline(order_id: str, product_id: str) -> list:
    """Pipeline para verificar si ya existe un detalle de orden para un producto específico"""
    return [
        {
            "$match": {
                "id_order": ObjectId(order_id),
                "id_inventory": ObjectId(product_id),
                "active": True
            }
        },
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]


def get_order_detail_by_id_pipeline(detail_id: str) -> list:
    """Pipeline para obtener un detalle específico de orden"""
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
        {"$project": {
            "_id": 1,
            "id_order": 1,
            "id_inventory": 1,
            "quantity": 1,
            "active": 1,
            "product_info": {"$arrayElemAt": ["$product_info", 0]},  # Verifica si no está vacío
            "order_info": {"$arrayElemAt": ["$order_info", 0]}  # Verifica si no está vacío
        }}
    ]

def get_order_details_owner_pipeline(order_id: str) -> list:
    """Pipeline para obtener el propietario de un detalle de orden"""
    return [
        {"$match": {"_id": ObjectId(order_id)}},
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
                "id_user": {"$arrayElemAt": ["$order_info.id_user", 0]}  # Extraemos el id del usuario
            }
        },
        {"$limit": 1}
    ] 