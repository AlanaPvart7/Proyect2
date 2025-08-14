from bson import ObjectId

def validate_catalog_type_pipeline(id_catalog_type: str) -> list:
    return [
        {"$match": {"_id": ObjectId(id_catalog_type), "active": True}},
        {"$limit": 1}
    ]

def get_catalog_with_type_pipeline(catalog_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(catalog_id), "active": True}},
        {"$lookup": {
            "from": "catalogtypes",
            "localField": "id_catalog_type",
            "foreignField": "_id",
            "as": "catalog_type"
        }},
        {"$unwind": "$catalog_type"},
        {"$project": {
            "id": {"$toString": "$_id"},
            "name": 1,
            "description": 1,
            "photo": 1,
            "cost": 1,
            "discount": 1,
            "active": 1,
            "id_catalog_type": {"$toString": "$id_catalog_type"},
            "catalog_type_description": "$catalog_type.description",
            "catalog_type_active": "$catalog_type.active",
            "id_artist": {"$toString": "$id_artist"}
        }}
    ]

def get_all_catalogs_with_types_pipeline(skip: int = 0, limit: int = 10) -> list:
    return [
        {"$match": {"active": True}},
        {"$lookup": {
            "from": "catalogtypes",
            "localField": "id_catalog_type",
            "foreignField": "_id",
            "as": "catalog_type"
        }},
        {"$unwind": "$catalog_type"},
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {
            "id": {"$toString": "$_id"},
            "name": 1,
            "description": 1,
            "photo": 1,
            "cost": 1,
            "discount": 1,
            "active": 1,
            "id_catalog_type": {"$toString": "$id_catalog_type"},
            "catalog_type_description": "$catalog_type.description",
            "catalog_type_active": "$catalog_type.active",
            "id_artist": {"$toString": "$id_artist"}
        }}
    ]

def get_catalogs_by_type_pipeline(catalog_type_description: str, skip: int = 0, limit: int = 10) -> list:
    return [
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
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {
            "id": {"$toString": "$_id"},
            "name": 1,
            "description": 1,
            "photo": 1,
            "cost": 1,
            "discount": 1,
            "active": 1,
            "id_catalog_type": {"$toString": "$id_catalog_type"},
            "catalog_type_description": "$catalog_type.description",
            "catalog_type_active": "$catalog_type.active",
            "id_artist": {"$toString": "$id_artist"}
        }}
    ]

def search_catalogs_pipeline(search_term: str, skip: int = 0, limit: int = 10) -> list:
    return [
        {"$match": {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ],
            "active": True
        }},
        {"$addFields": {
            "id_catalog_type_obj": {"$toObjectId": "$id_catalog_type"}
        }},
        {"$lookup": {
            "from": "catalogtypes",
            "localField": "id_catalog_type_obj",
            "foreignField": "_id",
            "as": "catalog_type"
        }},
        {"$unwind": "$catalog_type"},
        {"$project": {
            "id": {"$toString": "$_id"},
            "id_catalog_type": {"$toString": "$id_catalog_type"},
            "name": 1,
            "description": 1,
            "cost": 1,
            "discount": 1,
            "active": 1,
            "catalog_type_description": "$catalog_type.description",
            "id_artist": {"$toString": "$id_artist"}
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]
