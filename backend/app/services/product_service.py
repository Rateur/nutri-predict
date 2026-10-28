import duckdb
from typing import Optional
from app.schemas.product import ProductResponse
import os

class ProductService:
    def __init__(self) -> None:
        """
        Initialise la connexion DuckDB en mémoire.
        Le chemin du fichier Parquet doit pointer vers la donnée ingérée lors du pipeline de préparation.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.parquet_path = os.path.join(base_dir, "research", "data", "processed", "off_biscuits_fr.parquet")
        self.conn = duckdb.connect(database=':memory:')

    def get_product_by_barcode(self, barcode: str) -> Optional[ProductResponse]:
        """
        Exécute une requête SQL analytique via DuckDB sur le dataset Parquet.
        Extrait les données imbriquées (struct) pour correspondre au schéma Pydantic.
        """
        query = f"""
            SELECT 
                code, 
                product_name, 
                energy_kcal_100g, 
                sugars_100g
            FROM read_parquet('{self.parquet_path}')
            WHERE code = '{barcode}'
            LIMIT 1
        """
        try:
            result = self.conn.execute(query).fetchone()
            if result:
                return ProductResponse(
                    code=str(result[0]),
                    product_name=str(result[1]) if result[1] else "Nom indisponible",
                    energy_kcal_100g=float(result[2]) if result[2] is not None else None,
                    sugars_100g=float(result[3]) if result[3] is not None else None
                )
            return None
        except duckdb.Error as e:
            raise ValueError(f"Erreur d'exécution DuckDB : {str(e)}")
