from pydantic import BaseModel
from typing import Optional


class ProductOut(BaseModel):
    cod_producto: int
    desc_producto: str
    precio_neto: Optional[float] = None

    # extras (EXT)
    image_filename: Optional[str] = None
    is_featured: bool = False

    # Control de visibilidad (EXT)
    is_active: bool = True

    sort_order: Optional[int] = None
    notes: Optional[str] = None


class ProductExtraIn(BaseModel):
    image_filename: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    notes: Optional[str] = None


class ProductExtraOut(BaseModel):
    cod_producto: int
    image_filename: Optional[str] = None
    is_featured: bool = False
    is_active: bool = True
    sort_order: Optional[int] = None
    notes: Optional[str] = None
