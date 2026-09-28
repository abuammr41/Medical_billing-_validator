# Medical Billing Engine v2

Automated claim **pre-submission validation** and audit reporting (CSV / Excel in, Excel report out).

## Quick Start (Windows)

```
py -m pip install -r requirements.txt
py test_pipeline.py
py main.py sample_data.csv -o audit_report.xlsx
```

## What it checks

| Check | Rule |
|---|---|
| NPI | 10 digits, starts with 1 or 2, **official check digit** (Luhn with 80840 prefix) |
| Procedure code | CPT Category I (`99213`), Category II (`0521F`), Category III (`0042T`), HCPCS Level II (`J1885`) |
| ICD-10-CM | Valid format, with or without dot (`E11.9`, `E119`, `S72.001A`), auto-uppercased |
| Modifier | 2 characters each, max 4 (`25, 59`) |
| Units | Positive whole number |
| Place of Service | 2 digits |
| Date of Service | Valid date, not in the future; warning if older than timely-filing limit (365 days, configurable) |
| Amounts | Must be numeric and non-negative (`$1,250.00`, `(50)` handled) |
| Duplicates | Same patient + NPI + code + modifier + date of service → rejected |
| Code existence | Optional — drop official CMS code lists into `codes/` (see `codes/README.txt`) |

**Smart headers:** client files with headers like `NPI`, `CPT`, `HCPCS`, `ICD-10`, `Dx`, `Policy #`,
`Member ID`, `DOS`, `Charges` are recognized automatically (see `COLUMN_ALIASES` in `config.py`).
Leading zeros in IDs are preserved. UTF-8 / Excel (cp1252) CSV encodings supported.

## Billing math (simplified)

```
Base                  = Allowed Amount (if given) else Billed Amount
Coinsurance           = (Base - Copay - Deductible) x Coinsurance %
Patient Responsibility = Copay + Deductible + Coinsurance
Insurance Payable     = Base - Patient Responsibility      (0 for REJECTED claims)
```

## Report (Excel)

- **Summary** — totals, clean-claim rate, expected payable, top rejection reasons
- **Audit_Report** — every claim, green = ready, red = rejected, with issues and warnings
- **Rejected_Claims** — only the claims that need fixing

## Scope & Compliance

This is a **pre-submission format and data-quality validator**. It does not verify provider enrollment,
patient eligibility, payer-specific edits (NCCI/MUE, LCD/NCD), or actual adjudication/payment.
Production use needs clearinghouse/payer integrations and compliance review.

**PHI / HIPAA:** claim files and reports contain protected health information. Keep them on
encrypted, access-controlled storage; do not send them by unsecured email or chat.
