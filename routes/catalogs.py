from fastapi import APIRouter, Header, HTTPException, Depends, Query, Request
from typing import Optional
from models.catalogs import Catalog
from controllers import catalogs as catalogs_controller

router = APIRouter(prefix="/catalogs", tags=["🗃️ Catalogs"])

# Validación headers
async def validateadmin(admin: Optional[str] = Header(None)):
    if admin != "true":
        raise HTTPException(status_code=403, detail="Admin header requerido")

async def validateuser(user: Optional[str] = Header(None)):
    if user is None:
        raise HTTPException(status_code=403, detail="User header requerido")


# ---------------- Endpoints ---------------- #

@router.get("/search")
async def search_catalogs(
    q: str = Query(..., description="Término de búsqueda en nombre o descripción"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return await catalogs_controller.search_catalogs(q, skip, limit)


@router.get("/", summary="Listar todos los catálogos")
async def get_catalogs(skip: int = 0, limit: int = 10):
    return await catalogs_controller.get_catalogs(skip, limit)


@router.get("/{catalog_id}", summary="Obtener catálogo por ID")
async def get_catalog(catalog_id: str):
    return await catalogs_controller.get_catalog_by_id(catalog_id)


@router.post("/", summary="Crear un catálogo", dependencies=[Depends(validateadmin)])
async def create_catalog(catalog: Catalog, request: Request):
    return await catalogs_controller.create_catalog(catalog)


@router.put("/{catalog_id}", summary="Actualizar un catálogo", dependencies=[Depends(validateadmin)])
async def update_catalog(catalog_id: str, catalog: Catalog):
    return await catalogs_controller.update_catalog(catalog_id, catalog)


@router.delete("/{catalog_id}", summary="Desactivar un catálogo", dependencies=[Depends(validateadmin)])
async def deactivate_catalog(catalog_id: str):
    return await catalogs_controller.deactivate_catalog(catalog_id)
