from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class InventoryItem(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID"
    )
    id_catalog: str = Field(
        description="ID del catálogo al que pertenece el inventario"
    )
    stock: int = Field(
        description="Unidades disponibles",
        ge=0
    )
    entry_date: date = Field(
        description="Fecha de ingreso"
    )
    purchase_price: float = Field(
        description="Precio de compra",
        gt=0
    )
    sale_price: float = Field(
        description="Precio de venta",
        gt=0
    )
    observation: Optional[str] = Field(
        default="",
        description="Nota de ajuste"
    )
    active: bool = Field(
        default=True,
        description="Estado activo del registro"
    )

    reserved_quantity: Optional[int] = Field(
        default=0, 
        description="Cantidad reservada en órdenes activas"
        )
    
    available_stock: Optional[int] = Field(
        default=0, 
        description="Stock disponible (stock - reservado)"
        )

class CreateInventory(BaseModel):
    id_catalog: str
    stock: int = Field(ge=0)
    entry_date: date
    purchase_price: float = Field(gt=0)
    sale_price: float = Field(gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "id_catalog": "64e1234abcd56789ef0123456",
                "stock": 100,
                "entry_date": "2025-07-27",
                "purchase_price": 10.50,
                "sale_price": 15.00
            }
        }

class UpdateInventory(BaseModel):
    stock: Optional[int] = Field(ge=0)
    observation: Optional[str] = Field(default="")
