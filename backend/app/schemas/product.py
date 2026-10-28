from pydantic import BaseModel, Field
from typing import Optional

class ProductResponse(BaseModel):
    code: str = Field(..., description="Code barre unique du produit OpenFoodFacts")
    product_name: str = Field(..., description="Nom commercial du produit")
    energy_kcal_100g: Optional[float] = Field(None, description="Valeur énergétique pour 100g (kcal)")
    sugars_100g: Optional[float] = Field(None, description="Quantité de sucres pour 100g (g)")
