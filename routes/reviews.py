from fastapi import APIRouter, Request
from models.reviews import Review
from controllers.reviews import (
    get_reviews_by_catalog_id,
    create_review,
    update_review,
    delete_review
)
from utils.security import validateuser

router = APIRouter()

@router.get("/catalogs/{catalog_id}/reviews", response_model=list[Review], tags=["⭐ Reviews"])
async def get_reviews_for_catalog(catalog_id: str):
    """Obtener lista de reseñas de un catálogo"""
    return await get_reviews_by_catalog_id(catalog_id)

@router.post("/catalogs/{catalog_id}/reviews", response_model=Review, tags=["⭐ Reviews"])
@validateuser
async def create_review_for_catalog(catalog_id: str, request: Request, review: Review):
    review.id_user = request.state.id
    review.id_catalog = catalog_id
    return await create_review(review)


@router.put("/reviews/{review_id}", response_model=Review, tags=["⭐ Reviews"])
@validateuser
async def update_review_endpoint(request: Request, review_id: str, review: Review):
    """Actualizar una reseña existente"""
    return await update_review(review_id, review)

@router.delete("/reviews/{review_id}", response_model=Review, tags=["⭐ Reviews"])
@validateuser
async def delete_review_endpoint(request: Request, review_id: str):
    """Eliminar (soft delete) una reseña"""
    return await delete_review(review_id)