from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService
from app.core.auth import verify_api_key
from app.core.limiter import limiter

# Sécurisation du routeur avec l'authentification par clé d'API statique
router = APIRouter(dependencies=[Depends(verify_api_key)])

def get_product_service() -> ProductService:
    return ProductService()

@router.get("/{barcode}", response_model=ProductResponse)
@limiter.limit("15/minute")
def read_product(
    request: Request,
    barcode: str,
    service: ProductService = Depends(get_product_service)
) -> ProductResponse:
    """
    Exposition de la donnée OpenFoodFacts.
    Recherche un produit par son code-barres dans la base analytique Parquet.
    """
    try:
        product = service.get_product_by_barcode(barcode=barcode)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Produit introuvable dans le dataset OpenFoodFacts France."
        )
    return product

