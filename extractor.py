import os
import pandas as pd


def _read_csv_any_encoding(path, **kwargs):
    """Excel se bani CSV aksar utf-8-sig ya cp1252 hoti hai — sab try karo."""
    last_error = None
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, dtype=str, encoding=enc, keep_default_na=False, **kwargs)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error


def extract_claims_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    # Sab kuch TEXT ki tarah padho — taake NPI/policy/ZIP ke aage wale zero na mitein
    if ext == ".csv":
        df = _read_csv_any_encoding(file_path)
    elif ext in (".xls", ".xlsx"):
        df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
    elif ext in (".tsv", ".txt"):
        df = _read_csv_any_encoding(file_path, sep="\t")
    else:
        df = _read_csv_any_encoding(file_path, sep=None, engine="python")

    df = df.fillna("")
    # Poori khali rows hatao (Excel aksar aakhir mein khali rows chhod deta hai)
    df = df[~df.apply(lambda r: all(str(v).strip() == "" for v in r), axis=1)]
    return df.reset_index(drop=True)
