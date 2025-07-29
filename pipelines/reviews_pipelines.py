from bson import ObjectId

def get_reviews_by_catalog_pipeline(catalog_id: str) -> list:
    """Pipeline para obtener reviews activas de un catálogo con info de usuario y catálogo"""
    return [
        {"$match": {"id_catalog": catalog_id, "active": True}},
        {
            "$lookup": {
                "from": "users",
                "let": {"user_id": {"$toObjectId": "$id_user"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$user_id"]}}},
                    {"$project": {"_id": 0, "name": 1, "email": 1}}  # traer nombre y email usuario
                ],
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "catalogs",
                "let": {"catalog_id": {"$toObjectId": "$id_catalog"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$catalog_id"]}}},
                    {"$project": {"_id": 0, "title": 1, "description": 1}}  # título y descripción catálogo
                ],
                "as": "catalog_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_user": 1,
                "id_catalog": 1,
                "comment": 1,
                "rating": 1,
                "review_date": 1,
                "active": 1,
                "user_info": {"$arrayElemAt": ["$user_info", 0]},
                "catalog_info": {"$arrayElemAt": ["$catalog_info", 0]},
                "_id": 0
            }
        }
    ]

def get_review_by_id_pipeline(review_id: str) -> list:
    """Pipeline para obtener una review activa por id con info extra de usuario y catálogo"""
    return [
        {"$match": {"_id": ObjectId(review_id), "active": True}},
        {
            "$lookup": {
                "from": "users",
                "let": {"user_id": "$id_user"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$user_id"}]}}},
                    {"$project": {"_id": 0, "name": 1, "email": 1}}
                ],
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "catalogs",
                "let": {"catalog_id": "$id_catalog"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$catalog_id"}]}}},
                    {"$project": {"_id": 0, "title": 1, "description": 1}}
                ],
                "as": "catalog_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_user": 1,
                "id_catalog": 1,
                "comment": 1,
                "rating": 1,
                "review_date": 1,
                "active": 1,
                "user_info": {"$arrayElemAt": ["$user_info", 0]},
                "catalog_info": {"$arrayElemAt": ["$catalog_info", 0]},
                "_id": 0
            }
        }
    ]
