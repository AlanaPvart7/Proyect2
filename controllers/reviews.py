from fastapi import HTTPException
from bson import ObjectId, errors
from datetime import datetime
from utils.mongodb import get_collection
from models.reviews import Review
from pipelines.reviews_pipelines import get_reviews_by_catalog_pipeline, get_review_by_id_pipeline

coll = get_collection("reviews")

async def get_reviews_by_catalog_id(catalog_id: str) -> list[Review]:
    try:
        try:
            _ = ObjectId(catalog_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="ID de catálogo inválido")

        pipeline = get_reviews_by_catalog_pipeline(catalog_id)
        docs = list(coll.aggregate(pipeline))

        reviews = []
        for doc in docs:
            review_data = {k: doc[k] for k in Review._fields_.keys() if k in doc}
            reviews.append(Review(**review_data))

        return reviews
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reseñas: {str(e)}")

async def create_review(review: Review) -> Review:
    try:
        review.review_date = datetime.utcnow()
        review.active = True
        review_dict = review.model_dump(exclude={"id"})
        result = coll.insert_one(review_dict)
        review.id = str(result.inserted_id)
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear reseña: {str(e)}")

async def get_review_by_id(review_id: str) -> Review:
    try:
        try:
            _ = ObjectId(review_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="ID de reseña inválido")

        pipeline = get_review_by_id_pipeline(review_id)
        docs = list(coll.aggregate(pipeline))

        if not docs:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")

        review_data = {k: docs[0][k] for k in Review._fields_.keys() if k in docs[0]}
        return Review(**review_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reseña: {str(e)}")

async def update_review(review_id: str, review: Review) -> Review:
    try:
        try:
            _ = ObjectId(review_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="ID de reseña inválido")

        update_data = review.model_dump(exclude={"id", "id_user", "id_catalog", "review_date"})
        result = coll.update_one({"_id": ObjectId(review_id), "active": True}, {"$set": update_data})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")

        return await get_review_by_id(review_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar reseña: {str(e)}")

async def delete_review(review_id: str) -> Review:
    try:
        try:
            _ = ObjectId(review_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="ID de reseña inválido")

        result = coll.update_one({"_id": ObjectId(review_id)}, {"$set": {"active": False}})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")

        return await get_review_by_id(review_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar reseña: {str(e)}")