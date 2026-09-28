"""Tests — chalane ke 2 tareeqe:  py -m pytest -q   ya   py test_pipeline.py"""
import os
import tempfile

import openpyxl
import pandas as pd

import config
from calculator import calculate_billing_amounts, parse_money
from formatter import normalize_claim_columns
from main import run_pipeline
from validator import npi_check_digit_ok, validate_claim_row, validate_dataframe

GOOD = {"Provider_Npi": "1234567893", "Cpt_Code": "99213", "Icd10_Code": "E11.9", "Policy_Number": "POL123"}


def row(**kw):
    r = dict(GOOD); r.update(kw); return r


def test_valid_claim():
    assert validate_claim_row(GOOD)[0] == config.STATUS_READY


def test_npi_check_digit():
    assert npi_check_digit_ok("1234567893") and not npi_check_digit_ok("1234567890")
    assert validate_claim_row(row(Provider_Npi="1234567890"))[0] == config.STATUS_REJECTED
    assert "Invalid NPI format" in validate_claim_row(row(Provider_Npi="123"))[1]


def test_procedure_codes():
    for code in ("99213", "0521F", "0042T", "J1885", "G0439"):
        assert validate_claim_row(row(Cpt_Code=code))[0] == config.STATUS_READY, code
    for code in ("9921", "ABCDE", "Z1234", "992133"):
        assert validate_claim_row(row(Cpt_Code=code))[0] == config.STATUS_REJECTED, code


def test_icd10_codes():
    for code in ("E11.9", "I10", "S72.001A", "U07.1", "E119"):
        assert validate_claim_row(row(Icd10_Code=code))[0] == config.STATUS_READY, code
    for code in ("E11..9", "BAD", "11.9", "E1"):
        assert validate_claim_row(row(Icd10_Code=code))[0] == config.STATUS_REJECTED, code


def test_optional_fields():
    assert "Modifier" in validate_claim_row(row(Modifier="XYZ"))[1]
    assert validate_claim_row(row(Modifier="25, 59"))[0] == config.STATUS_READY
    assert "Units" in validate_claim_row(row(Units="0"))[1]
    assert "future" in validate_claim_row(row(Date_Of_Service="2099-01-01"))[1]
    assert "timely filing" in validate_claim_row(row(Date_Of_Service="2020-01-01"))[2]
    assert "Negative" in validate_claim_row(row(Billed_Amount="-$10"))[1]


def test_column_aliases_and_uppercase():
    df = pd.DataFrame([{"NPI": "1234567893", "CPT": "j1885", "ICD-10": "e11.9", "Policy #": "00123"}])
    df = normalize_claim_columns(df)
    assert list(df.columns)[:4] == ["Provider_Npi", "Cpt_Code", "Icd10_Code", "Policy_Number"]
    assert df.iloc[0]["Cpt_Code"] == "J1885" and df.iloc[0]["Policy_Number"] == "00123"


def test_money_parsing():
    assert parse_money("$1,250.50") == 1250.5 and parse_money("(50)") == -50.0 and parse_money("") is None


def test_billing_math_with_coinsurance():
    df = pd.DataFrame([{"Billed_Amount": "$250", "Allowed_Amount": "$180", "Copay": "20", "Deductible": "30",
                        "Coinsurance_Pct": "20%", "Validation_Status": config.STATUS_READY}])
    r = calculate_billing_amounts(df).iloc[0]
    # base 180; after copay+ded = 130; coins 26; patient 76; payable 104
    assert r["Patient_Responsibility"] == 76.0 and r["Insurance_Payable"] == 104.0


def test_rejected_claim_payable_zero():
    df = pd.DataFrame([{"Billed_Amount": "$250", "Copay": "0", "Deductible": "0", "Validation_Status": config.STATUS_REJECTED}])
    assert calculate_billing_amounts(df).iloc[0]["Insurance_Payable"] == 0.0


def test_duplicate_claims():
    df = pd.DataFrame([dict(GOOD, Patient_Id="P1", Date_Of_Service="2026-09-01"),
                       dict(GOOD, Patient_Id="P1", Date_Of_Service="2026-09-01")])
    out = validate_dataframe(df)
    assert out.iloc[0]["Validation_Status"] == config.STATUS_READY
    assert "Duplicate" in out.iloc[1]["Validation_Issues"]


def test_full_pipeline_sample():
    here = os.path.dirname(os.path.abspath(__file__))
    fd, out = tempfile.mkstemp(suffix=".xlsx"); os.close(fd)
    df, out = run_pipeline(os.path.join(here, "sample_data.csv"), out)
    status = dict(zip(df["Claim_Id"], df["Validation_Status"]))
    assert [status[k] for k in ("CLM001", "CLM002", "CLM003")] == [config.STATUS_READY] * 3
    assert all(status[k] == config.STATUS_REJECTED for k in ("CLM004", "CLM005", "CLM006", "CLM007"))
    assert df.loc[df["Claim_Id"] == "CLM001", "Policy_Number"].iloc[0] == "00123"
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == ["Summary", "Audit_Report", "Rejected_Claims"]
    os.remove(out)


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\nALL {len(tests)} TESTS PASSED")
