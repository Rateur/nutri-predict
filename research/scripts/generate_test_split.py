import os
import pandas as pd
from sklearn.model_selection import train_test_split

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'processed')
    source_path = os.path.join(data_dir, 'ml_training_dataset.parquet')
    
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file {source_path} not found.")

    print(f"Loading {source_path}...")
    df = pd.read_parquet(source_path)
    
    print("Splitting dataset 80/20...")
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    train_path = os.path.join(data_dir, 'ml_training_dataset.parquet')
    test_path = os.path.join(data_dir, 'ml_test_dataset.parquet')
    
    print(f"Saving training set ({len(train_df)} rows) to {train_path}...")
    train_df.to_parquet(train_path, index=False)
    
    print(f"Saving testing set ({len(test_df)} rows) to {test_path}...")
    test_df.to_parquet(test_path, index=False)
    
    print("Done!")

if __name__ == '__main__':
    main()
