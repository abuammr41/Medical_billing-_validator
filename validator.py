import math
import os
import re
from datetime import datetime

import pandas as pd

import config
from calculator import parse_money

_CODE_CACHE = {}


def npi_check_digit_ok(npi):
    """NPI ka asli check-digit test (Luhn, CMS ka '80840' prefix ke sath)."""
    if not re.fullmatch(r"\d{10}", npi) or npi[0] not in "12":
        return False
    digits = [int(d) for d in "80840" + npi]
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _load_code_list(filename, pattern):
    """
    Optional: codes/ folder mein CMS ki code list ho to code ka ASLI wujood check hota hai.
    Har line ka pehla code-jaisa token liya jata hai (CMS order file ka number skip hota hai).
    """
    if filename in _CODE_CACHE:
        return _CODE_CACHE[filename]
    path = os.path.join(config.CODES_DIR, filename)
    codes = None
    if os.path.exists(path):
        codes = set()
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                for token in line.split():
                    token = token.strip().upper().replace(".", "")
                    if re.fullmatch(pattern, token):
                        codes.add(token)
                        break
    _CODE_CACHE[filename] = codes
    return codes


def _is_missing(value):
    return str(value if value is not None else "").strip() == ""


def validate_claim_row(row):
    """Return (status, issues_text, warnings_text). Issues = reject, warnings = sirf khabar."""
    issues, warnings = [], []
    get = lambda c: str(row.get(c, "") if row.get(c, "") is not None else "").strip()

    for col in config.REQUIRED_CLAIM_COLUMNS:
        if _is_missing(row.get(col, "")):
            issues.append(f"Missing {col}")

    npi, proc, icd = get("Provider_Npi"), get("Cpt_Code").upper(), get("Icd10_Code").upper()

    if npi:
        if not re.fullmatch(r"\d{10}", npi):
            issues.append("Invalid NPI format (must be 10 digits)")
        elif not npi_check_digit_ok(npi):
            issues.append("Invalid NPI (check digit failed or does not start with 1/2)")

    if proc:
        if not config.PROCEDURE_PATTERN.fullmatch(proc):
            issues.append("Invalid CPT/HCPCS format")
        else:
            cpt_list = _load_code_list("cpt_codes.txt", r"\d{4}[0-9FT]")
            hcpcs_list = _load_code_list("hcpcs_codes.txt", r"[A-V]\d{4}")
            known = cpt_list if proc[0].isdigit() else hcpcs_list
            if known is not None and proc not in known:
                issues.append(f"Code {proc} not found in code list")

    if icd:
        if not config.ICD10_PATTERN.fullmatch(icd):
            issues.append("Invalid ICD-10 format")
        else:
            icd_list = _load_code_list("icd10_codes.txt", r"[A-Z]\d[0-9A-Z]{1,5}")
            if icd_list is not None and icd.replace(".", "") not in icd_list:
                issues.append(f"ICD-10 {icd} not found in code list (or not billable)")

    mods = get("Modifier")
    if mods:
        parts = [m for m in re.split(r"[,;:/\s]+", mods.upper()) if m]
        if len(parts) > 4 or any(not config.MODIFIER_PATTERN.fullmatch(m) for m in parts):
            issues.append("Invalid Modifier (2 characters, max 4)")

    units = get("Units")
    if units:
        try:
            u = float(units)
            if u <= 0 or u != int(u):
                issues.append("Invalid Units (must be a positive whole number)")
        except ValueError:
            issues.append("Invalid Units (must be a positive whole number)")

    pos = get("Place_Of_Service")
    if pos and not config.POS_PATTERN.fullmatch(pos.zfill(2)):
        issues.append("Invalid Place of Service (2 digits)")

    dos = get("Date_Of_Service")
    if dos:
        parsed = pd.to_datetime(dos, errors="coerce")
        if pd.isna(parsed):
            issues.append("Invalid Date of Service")
        else:
            today = pd.Timestamp(datetime.now().date())
            if parsed > today:
                issues.append("Date of Service is in the future")
            elif (today - parsed).days > config.TIMELY_FILING_DAYS:
                warnings.append(f"DOS older than {config.TIMELY_FILING_DAYS} days (timely filing risk)")

    for col in config.MONEY_COLUMNS:
        raw = row.get(col, "")
        if _is_missing(raw):
            continue
        val = parse_money(raw)
        if val is None:
            continue
        if isinstance(val, float) and math.isnan(val):
            issues.append(f"Invalid amount in {col}")
        elif val < 0:
            issues.append(f"Negative amount in {col}")

    coins = get("Coinsurance_Pct").replace("%", "")
    if coins:
        c = parse_money(coins)
        if c is None or (isinstance(c, float) and math.isnan(c)) or not 0 <= c <= 100:
            issues.append("Invalid Coinsurance % (0-100)")

    billed, allowed = parse_money(row.get("Billed_Amount", "")), parse_money(row.get("Allowed_Amount", ""))
    if isinstance(billed, float) and isinstance(allowed, float) and not math.isnan(billed) and not math.isnan(allowed) and allowed > billed:
        warnings.append("Allowed amount is higher than billed amount")

    status = config.STATUS_REJECTED if issues else config.STATUS_READY
    return status, "; ".join(issues) or "None", "; ".join(warnings) or "None"


def validate_dataframe(df):
    df = df.copy()
    results = [validate_claim_row(row) for _, row in df.iterrows()]
    df["Validation_Status"] = [r[0] for r in results]
    df["Validation_Issues"] = [r[1] for r in results]
    df["Warnings"] = [r[2] for r in results]

    # Duplicate claims — pehli dafa theek, baad wali REJECTED
    key_cols = [c for c in config.DUPLICATE_KEY_COLUMNS if c in df.columns]
    if len(key_cols) < 3:
        key_cols = [c for c in df.columns if c not in ("Validation_Status", "Validation_Issues", "Warnings")]
    if len(df) and key_cols:
        keys = df[key_cols].astype(str).apply(lambda r: "|".join(v.strip().upper() for v in r), axis=1)
        first_seen = {}
        for idx, key in keys.items():
            if key.replace("|", "") == "":
                continue
            if key in first_seen:
                note = f"Duplicate claim (same as row {first_seen[key] + 2})"
                prev = df.at[idx, "Validation_Issues"]
                df.at[idx, "Validation_Issues"] = note if prev == "None" else f"{prev}; {note}"
                df.at[idx, "Validation_Status"] = config.STATUS_REJECTED
            else:
                first_seen[key] = idx
    return df
