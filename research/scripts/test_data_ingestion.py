import sys
import os
import duckdb
import pytest

# Ajout de la racine au sys.path pour importer research.scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from research.scripts.ingest_off import ingest_off_parquet

def test_ingest_off_parquet_e2e():
    """
    Test de bout en bout de l'ingestion de données OpenFoodFacts.
    Vérifie l'exécution, la création physique du fichier Parquet et la validité du schéma via DuckDB.
    """
    processed_parquet = os.path.join("research", "data", "processed", "off_biscuits_fr.parquet")
    
    # Étape 1 : Exécution physique de l'ingestion (sans mocks réseau)
    # Note : Cela téléchargera réellement les données depuis Hugging Face
    try:
        ingest_off_parquet()
    except Exception as e:
        pytest.fail(f"L'ingestion a échoué : {str(e)}")

    # Étape 2 : Vérification de l'existence du fichier
    assert os.path.exists(processed_parquet), f"Le fichier Parquet {processed_parquet} n'a pas été créé."

    # Étape 3 : Validation du contenu via DuckDB
    con = duckdb.connect(database=":memory:")
    try:
        # Lecture du fichier Parquet
        query = f"SELECT * FROM read_parquet('{processed_parquet}')"
        res = con.execute(query)
        
        # Récupération des colonnes et des lignes
        columns = [desc[0] for desc in res.description]
        rows = res.fetchall()
        
        # Vérifications
        assert len(rows) > 0, "Le fichier Parquet est vide."
        
        # Vérification des colonnes essentielles
        assert "product_name" in columns, "La colonne 'product_name' est manquante dans le schéma Parquet."
        assert "code" in columns, "La colonne 'code' est manquante dans le schéma Parquet."
        
        # Vérification optionnelle des types (DuckDB s'en charge généralement au schéma)
        print(f"Validation terminée : {len(rows)} lignes trouvées avec les colonnes {columns}")
        
    finally:
        con.close()

if __name__ == "__main__":
    test_ingest_off_parquet_e2e()
