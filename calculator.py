import math
import re
import pandas as pd
import config


def parse_money(value):
    """
    "$1,250.00" -> 1250.0, "(50)" -> -50.0, "" -> None (khali), "abc" -> NaN (ghalat).
    """
    s = str(value if value is not None else "").strip()
    if s == "" or s.lower() in ("nan", "none", "n/a"):
        return None
    negative = s.startswith("(") and s.endswith(")")
    s = re.sub(r"(?i)usd|pkr|rs\.?|\$|,|\s|\(|\)", "", s)
    try:
        num = float(s)
    except ValueError:
        return float("nan")
    return -num if negative else num


def _money_series(df, col):
    if col not in df.columns:
        return pd.Series([0.0] * len(df), index=df.index)
    vals = df[col].apply(parse_money)
    return vals.apply(lambda v: 0.0 if v is None or (isinstance(v, float) and math.isnan(v)) else v)


def calculate_billing_amounts(df):
    """
    Simplified payer math (demo — asli payer contract rules alag ho sakte hain):
      Base      = Allowed_Amount (agar ho) warna Billed_Amount
      Coinsurance = (Base - Copay - Deductible) x Coinsurance_Pct%
      Patient_Responsibility = Copay + Deductible + Coinsurance  (Base se zyada nahi)
      Insurance_Payable      = Base - Patient_Responsibility
    REJECTED claims par payable 0 — ghalat claim ka payment dikhana gumrah karta hai.
    """
    df = df.copy()
    for col in ("Billed_Amount", "Copay", "Deductible"):
        df[col] = _money_series(df, col)

    base = df["Billed_Amount"].copy()
    if "Allowed_Amount" in df.columns:
        allowed = _money_series(df, "Allowed_Amount")
        has_allowed = df["Allowed_Amount"].astype(str).str.strip() != ""
        df["Allowed_Amount"] = allowed
        base = base.where(~has_allowed, allowed)

    coins_pct = pd.Series([0.0] * len(df), index=df.index)
    if "Coinsurance_Pct" in df.columns:
        coins_pct = df["Coinsurance_Pct"].astype(str).str.replace("%", "", regex=False).apply(parse_money)
        coins_pct = coins_pct.apply(lambda v: 0.0 if v is None or (isinstance(v, float) and math.isnan(v)) else v)
        df["Coinsurance_Pct"] = coins_pct

    after_fixed = (base - df["Copay"] - df["Deductible"]).clip(lower=0)
    coinsurance = (after_fixed * coins_pct / 100).round(2)
    patient = (df["Copay"] + df["Deductible"] + coinsurance).clip(upper=base.clip(lower=0))
    payable = (base - patient).clip(lower=0).round(2)

    ready = df.get("Validation_Status", pd.Series([config.STATUS_READY] * len(df), index=df.index)) == config.STATUS_READY
    df["Patient_Responsibility"] = patient.round(2).where(ready, 0.0)
    df["Insurance_Payable"] = payable.where(ready, 0.0)
    return df
