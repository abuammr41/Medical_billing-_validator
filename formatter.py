import re
import pandas as pd
import config


def _key(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def map_columns(df):
    """Client ke headers (NPI, CPT, ICD-10, Policy #...) ko standard naamon par lao."""
    lookup = {}
    for standard, aliases in config.COLUMN_ALIASES.items():
        lookup[_key(standard)] = standard
        for alias in aliases:
            lookup[alias] = standard

    renamed, used = {}, set()
    for col in df.columns:
        std = lookup.get(_key(col))
        if std and std not in used:
            renamed[col] = std
            used.add(std)
    return df.rename(columns=renamed)


def normalize_claim_columns(df):
    df = map_columns(df.copy())
    df.columns = [str(c).strip() for c in df.columns]

    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # Codes hamesha BARE huroof mein (e11.9 -> E11.9, j1885 -> J1885)
    for col in ("Cpt_Code", "Icd10_Code", "Modifier"):
        if col in df.columns:
            df[col] = df[col].str.upper().str.replace(" ", "", regex=False)
    if "Provider_Npi" in df.columns:
        df["Provider_Npi"] = df["Provider_Npi"].str.replace(r"[\s-]", "", regex=True)
    return df
