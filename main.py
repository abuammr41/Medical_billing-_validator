import argparse
import sys
import time

import config
from calculator import calculate_billing_amounts
from exporter import export_audit_report
from extractor import extract_claims_data
from formatter import normalize_claim_columns
from validator import validate_dataframe


def run_pipeline(input_file, output_file):
    df = extract_claims_data(input_file)
    df = normalize_claim_columns(df)
    df = validate_dataframe(df)
    df = calculate_billing_amounts(df)
    output_file = export_audit_report(df, output_file)
    return df, output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Medical billing claim validation engine")
    parser.add_argument("input_file", help="Input CSV / XLSX / XLS / TSV file")
    parser.add_argument("-o", "--output", default="audit_report.xlsx", help="Output Excel report")
    args = parser.parse_args()

    start = time.time()
    try:
        result, out = run_pipeline(args.input_file, args.output)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    ready = int((result["Validation_Status"] == config.STATUS_READY).sum())
    print("==========================================")
    print("   MEDICAL BILLING VALIDATION COMPLETED")
    print("==========================================")
    print(f"Claims processed : {len(result)}")
    print(f"Ready to submit  : {ready}")
    print(f"Rejected         : {len(result) - ready}")
    print(f"Time             : {time.time() - start:.2f} seconds")
    print(f"Report           : {out}")
