import pandas as pd


def parse_tsv(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, sep='\t')
    return df
