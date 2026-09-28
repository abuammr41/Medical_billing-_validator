"""
Medical Billing Engine — settings.
Sab rules yahan hain, code chhede baghair badle ja sakte hain.
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODES_DIR = os.path.join(BASE_DIR, "codes")   # optional CMS code lists (README dekho)

# ---------- Code formats ----------
# CPT Category I (5 digits), Category II (4 digits + F), Category III (4 digits + T),
# HCPCS Level II (A-V + 4 digits, jaise J1885, G0439)
PROCEDURE_PATTERN = re.compile(r"^(\d{5}|\d{4}[FT]|[A-V]\d{4})$")
# ICD-10-CM: letter + digit + alphanumeric, phir optional dot + 1-4 characters (E11.9, I10, S72.001A)
ICD10_PATTERN = re.compile(r"^[A-Z]\d[0-9A-Z](\.?[0-9A-Z]{1,4})?$")
MODIFIER_PATTERN = re.compile(r"^[0-9A-Z]{2}$")
POS_PATTERN = re.compile(r"^\d{2}$")

# ---------- Columns ----------
REQUIRED_CLAIM_COLUMNS = ["Provider_Npi", "Cpt_Code", "Icd10_Code", "Policy_Number"]
MONEY_COLUMNS = ["Billed_Amount", "Allowed_Amount", "Copay", "Deductible"]

# Client ki file mein header kuch bhi ho sakta hai — sab ek standard naam par aa jate hain.
# (chhote huroof, sirf a-z0-9 — space, _, -, #, . sab hata kar match hota hai)
COLUMN_ALIASES = {
    "Provider_Npi": ["providernpi", "npi", "renderingnpi", "billingnpi", "npinumber", "providerid"],
    "Cpt_Code": ["cptcode", "cpt", "procedurecode", "hcpcs", "hcpcscode", "cpthcpcs", "proccode", "procedure"],
    "Icd10_Code": ["icd10code", "icd10", "icd", "icdcode", "diagnosiscode", "dxcode", "diagnosis", "dx", "primarydiagnosis"],
    "Policy_Number": ["policynumber", "policy", "policyno", "memberid", "subscriberid", "insuranceid", "policyid"],
    "Billed_Amount": ["billedamount", "billed", "chargeamount", "charges", "charge", "totalcharge", "amount"],
    "Allowed_Amount": ["allowedamount", "allowed", "contractamount"],
    "Copay": ["copay", "copayment", "copayamount"],
    "Deductible": ["deductible", "deductibleamount"],
    "Coinsurance_Pct": ["coinsurancepct", "coinsurance", "coinsurancepercent", "coinspct"],
    "Date_Of_Service": ["dateofservice", "dos", "servicedate", "dateofservicefrom"],
    "Modifier": ["modifier", "modifiers", "mod"],
    "Units": ["units", "unit", "quantity", "qty"],
    "Place_Of_Service": ["placeofservice", "pos", "poscode"],
    "Patient_Id": ["patientid", "patientaccount", "accountnumber", "mrn", "patientno"],
    "Claim_Id": ["claimid", "claimnumber", "claimno"],
}

# Duplicate claim pehchanne ke liye (jo columns file mein hon, sirf wahi use hote hain)
DUPLICATE_KEY_COLUMNS = ["Patient_Id", "Provider_Npi", "Cpt_Code", "Modifier", "Date_Of_Service"]

# Date of service kitni purani ho sakti hai (din) — aam tor par payers 90-365 din dete hain
TIMELY_FILING_DAYS = 365

STATUS_READY = "READY_TO_SUBMIT"
STATUS_REJECTED = "REJECTED"
