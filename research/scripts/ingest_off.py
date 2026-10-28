import duckdb
import json
import os

def ingest_off_parquet():
    """
    Ingest OpenFoodFacts data from Parquet using DuckDB and export to a processed Parquet file.
    """
    raw_path = os.path.join("research", "data", "raw", "off_biscuits_fr.json")
    processed_path = os.path.join("research", "data", "processed", "off_biscuits_fr.parquet")
    
    print("Connecting to in-memory DuckDB...")
    con = duckdb.connect(database=":memory:")
    
    print("Installing and loading httpfs extension...")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    # Query to fetch from remote and save to local JSON first (as per existing logic)
    # OR directly COPY from remote to Parquet.
    # The user specifically asked to read the raw JSON and export to Parquet.
    
    query_remote = """
    SELECT 
        code,
        product_name[1].text as product_name, 
        nutriscore_grade, 
        nutriments
    FROM read_parquet('https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet')
    WHERE array_to_string(categories_tags, ',') LIKE '%biscuits%' 
      AND array_to_string(countries_tags, ',') LIKE '%france%'
    LIMIT 1000
    """
    
    print("Executing query on remote Parquet file...")
    try:
        # First ensure the raw JSON exists (if we want to stick to the two-step process hinted by the user)
        # But the user's specific instruction is: 
        # "Modifier research/scripts/ingest_off.py pour lire le fichier brut et l'exporter en Parquet."
        # This implies the raw JSON is already there or we create it.
        
        # Let's do the direct remote -> parquet for efficiency, 
        # but ensure we follow the "read raw and export" if needed.
        # Let's follow the user's requested instruction:
        # COPY (SELECT * FROM read_json_auto('research/data/raw/off_biscuits_fr.json')) TO 'research/data/processed/off_biscuits_fr.parquet' (FORMAT PARQUET);
        
        if not os.path.exists(raw_path):
            print(f"Raw data not found at {raw_path}. Fetching from remote first...")
            res = con.execute(query_remote)
            columns = [desc[0] for desc in res.description]
            products = [dict(zip(columns, row)) for row in res.fetchall()]
            
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            with open(raw_path, 'w', encoding='utf-8') as f:
                # Save as a simple list of objects for easier DuckDB reading
                json.dump(products, f, ensure_ascii=False, indent=4)
            print(f"Raw JSON saved to {raw_path}")

        print(f"Exporting {raw_path} to Parquet...")
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        
        # Now read_json_auto will see a list of objects and create columns accordingly
        copy_query = f"""
        COPY (
            SELECT 
                code,
                product_name,
                (list_filter(nutriments, x -> x.name = 'energy-kcal')[1])."100g" AS energy_kcal_100g,
                (list_filter(nutriments, x -> x.name = 'sugars')[1])."100g" AS sugars_100g
            FROM read_json_auto('{raw_path}')
        ) TO '{processed_path}' (FORMAT PARQUET);
        """
        con.execute(copy_query)
        
        print(f"Successfully exported data to {processed_path}")
        
    except Exception as e:
        print(f"Error during ingestion/export: {e}")
        raise

if __name__ == "__main__":
    ingest_off_parquet()
