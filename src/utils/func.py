import pandas as pd

def importData(path: str) -> pd.DataFrame:
    """Import app dataset from either parquet, csv, or xlsx"""
    if path.endswith('.parquet'):
        return pd.read_parquet(path)

    elif path.endswith('.csv'):
        return pd.read_csv(path)
    
    elif path.endswith('.xlsx'):
        return pd.read_excel(path)
    
    else:
        raise Exception("FileError: No suitable dataset found")