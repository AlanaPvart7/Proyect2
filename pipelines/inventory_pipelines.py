from bson import ObjectId
from utils.mongodb import get_collection

coll = get_collection("inventory")

def get_inventory_pipeline(skip: int = 0, limit: int = 10, available_only: bool = False):
    pipeline = [
        {"$match": {"active": True}}
    ]

    if available_only:
        pipeline[0]["$match"]["stock"] = {"$gt": 0}

    pipeline.append({"$sort": {"entry_date": -1}})

    if skip > 0:
        pipeline.append({"$skip": skip})

    # Solo agregar $limit si es un entero positivo
    if isinstance(limit, int) and limit > 0:
        pipeline.append({"$limit": limit})

    pipeline.extend([
        {
            "$lookup": {
                "from": "catalogs",
                "localField": "id_catalog",
                "foreignField": "_id",
                "as": "catalog_info"
            }
        },
        {"$unwind": {"path": "$catalog_info", "preserveNullAndEmptyArrays": True}}
    ])

    return pipeline

def get_active_order_status_ids() -> list:
    """
    Devuelve los id_status (string) de estados de órdenes activas
    que reservan stock (ejemplo: 'inprogress', 'ordered', 'processing').
    """
    return [
        "64e8a07d1234567890abcdef",  # inprogress
        "64e8a07d2234567890abcdef",  # ordered
        "64e8a07d3234567890abcdef",  # processing
    ]

def get_all_inventory_pipeline(skip: int = 0, limit: int | None = 50) -> list:
    pipeline = [
        {"$match": {"active": True}},

        {
            "$lookup": {
                "from": "catalogs",
                "let": {"catalog_id": {"$toObjectId": "$id_catalog"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$catalog_id"]}}},
                    {"$project": {"description": 1, "price": 1, "_id": 0}}
                ],
                "as": "catalog_info"
            }
        },
        {"$unwind": {"path": "$catalog_info", "preserveNullAndEmptyArrays": True}},

        {
            "$lookup": {
                "from": "order_details",
                "let": {"inventory_id": {"$toString": "$_id"}},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {"$eq": ["$id_inventory", "$$inventory_id"]},
                            "active": True
                        }
                    },
                    {
                        "$lookup": {
                            "from": "order_status_record",
                            "let": {"order_id": "$id_order"},
                            "pipeline": [
                                {"$match": {"$expr": {"$eq": ["$id_order", "$$order_id"]}}},
                                {"$sort": {"date": -1}},
                                {"$limit": 1},
                                {"$match": {"id_status": {"$in": get_active_order_status_ids()}}}
                            ],
                            "as": "latest_status"
                        }
                    },
                    {"$unwind": {"path": "$latest_status", "preserveNullAndEmptyArrays": False}},
                    {
                        "$group": {
                            "_id": None,
                            "reserved_quantity": {"$sum": "$quantity"}
                        }
                    }
                ],
                "as": "reserved_stock_info"
            }
        },

        {
            "$addFields": {
                "reserved_quantity": {
                    "$ifNull": [{"$arrayElemAt": ["$reserved_stock_info.reserved_quantity", 0]}, 0]
                },
                "available_stock": {
                    "$subtract": [
                        "$stock",
                        {"$ifNull": [{"$arrayElemAt": ["$reserved_stock_info.reserved_quantity", 0]}, 0]}
                    ]
                }
            }
        },

        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_catalog": 1,
                "stock": 1,
                "entry_date": 1,
                "purchase_price": 1,
                "sale_price": 1,
                "observation": 1,
                "active": 1,
                "catalog_description": "$catalog_info.description",
                "catalog_price": "$catalog_info.price",
                "reserved_quantity": 1,
                "available_stock": 1,
                "_id": 0
            }
        },

        {"$sort": {"entry_date": -1}},
    ]

    if skip > 0:
        pipeline.append({"$skip": skip})

    if isinstance(limit, int) and limit > 0:
        pipeline.append({"$limit": limit})

    return pipeline

def get_inventory_by_id_pipeline(inventory_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(inventory_id), "active": True}},

        {
            "$lookup": {
                "from": "catalogs",
                "let": {"catalog_id": {"$toObjectId": "$id_catalog"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$catalog_id"]}}},
                    {"$project": {"description": 1, "price": 1, "_id": 0}}
                ],
                "as": "catalog_info"
            }
        },
        {"$unwind": {"path": "$catalog_info", "preserveNullAndEmptyArrays": True}},

        {
            "$lookup": {
                "from": "order_details",
                "let": {"inventory_id": {"$toString": "$_id"}},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {"$eq": ["$id_inventory", "$$inventory_id"]},
                            "active": True
                        }
                    },
                    {
                        "$lookup": {
                            "from": "order_status_record",
                            "let": {"order_id": "$id_order"},
                            "pipeline": [
                                {"$match": {"$expr": {"$eq": ["$id_order", "$$order_id"]}}},
                                {"$sort": {"date": -1}},
                                {"$limit": 1},
                                {"$match": {"id_status": {"$in": get_active_order_status_ids()}}}
                            ],
                            "as": "latest_status"
                        }
                    },
                    {"$unwind": {"path": "$latest_status", "preserveNullAndEmptyArrays": False}},
                    {
                        "$group": {
                            "_id": None,
                            "reserved_quantity": {"$sum": "$quantity"}
                        }
                    }
                ],
                "as": "reserved_stock_info"
            }
        },

        {
            "$addFields": {
                "reserved_quantity": {
                    "$ifNull": [{"$arrayElemAt": ["$reserved_stock_info.reserved_quantity", 0]}, 0]
                },
                "available_stock": {
                    "$subtract": [
                        "$stock",
                        {"$ifNull": [{"$arrayElemAt": ["$reserved_stock_info.reserved_quantity", 0]}, 0]}
                    ]
                }
            }
        },

        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_catalog": 1,
                "stock": 1,
                "entry_date": 1,
                "purchase_price": 1,
                "sale_price": 1,
                "observation": 1,
                "active": 1,
                "catalog_description": "$catalog_info.description",
                "catalog_price": "$catalog_info.price",
                "reserved_quantity": 1,
                "available_stock": 1,
                "_id": 0
            }
        }
    ]

def validate_catalog_pipeline(catalog_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(catalog_id)}},
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]
