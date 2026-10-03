"""Generate a realistic (fully synthetic) demo claims batch for the Medical Billing Engine portfolio sample."""
import sys, os, csv, random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validator import npi_check_digit_ok

random.seed(42)
OUTDIR = os.path.dirname(os.path.abspath(__file__))

def make_npi(prefix_digit):
    for _ in range(2000):
        body = str(prefix_digit) + "".join(str(random.randint(0, 9)) for _ in range(8))
        for d in range(10):
            cand = body + str(d)
            if npi_check_digit_ok(cand):
                return cand
    raise RuntimeError("could not build NPI")

PROVIDERS = [make_npi(1) for _ in range(4)]

CPT_POOL = [
    ("99213", 150.0, "Office visit, established, low"),
    ("99214", 220.0, "Office visit, established, moderate"),
    ("99212", 110.0, "Office visit, established, minimal"),
    ("99203", 190.0, "Office visit, new patient, low"),
    ("99395", 240.0, "Preventive visit, adult"),
    ("36415", 15.0, "Venipuncture"),
    ("93000", 55.0, "EKG with interpretation"),
    ("J1885", 28.0, "Injection, ketorolac"),
    ("0521F", 0.0, "Quality measure: tobacco screening"),
]

ICD_POOL = ["E11.9", "I10", "M54.5", "J06.9", "Z00.00", "E78.5", "K21.9", "F41.1", "M25.561", "R51"]
MODIFIERS = ["", "", "", "25", "59", "RT", "LT"]
POS_POOL = ["11", "11", "11", "22", "02"]

today = date(2026, 9, 28)

rows = []
cid = 1
pid = 1001

def next_ids():
    global cid, pid
    c = f"CLM{cid:04d}"
    p = f"P{pid:04d}"
    cid += 1
    pid += 1
    return c, p

N_CLEAN = 128
for _ in range(N_CLEAN):
    claim_id, patient_id = next_ids()
    cpt, base_amt, _ = random.choice(CPT_POOL)
    npi = random.choice(PROVIDERS)
    icd = random.choice(ICD_POOL)
    mod = random.choice(MODIFIERS)
    units = 1 if cpt != "36415" else random.choice([1, 1, 2])
    dos = today - timedelta(days=random.randint(0, 45))
    billed = round(base_amt * random.uniform(0.92, 1.12), 2)
    allowed = round(billed * random.uniform(0.6, 0.85), 2)
    copay = random.choice([0, 15, 20, 25, 30])
    deductible = random.choice([0, 0, 0, 25, 50])
    coins = random.choice([0, 10, 20])
    rows.append({
        "Claim ID": claim_id, "Patient ID": patient_id, "NPI": npi, "CPT": cpt,
        "Modifier": mod, "Units": units, "ICD-10": icd,
        "Policy #": f"POL{random.randint(10000, 99999)}",
        "Date of Service": dos.isoformat(), "POS": random.choice(POS_POOL),
        "Billed Amount": f"${billed:.2f}", "Allowed Amount": f"${allowed:.2f}",
        "Copay": copay, "Deductible": deductible, "Coinsurance %": coins,
    })

# a few claims with an old (but within-range) DOS -> timely-filing warning, still ready
for _ in range(4):
    claim_id, patient_id = next_ids()
    cpt, base_amt, _ = random.choice(CPT_POOL)
    npi = random.choice(PROVIDERS)
    billed = round(base_amt * random.uniform(0.95, 1.1), 2)
    rows.append({
        "Claim ID": claim_id, "Patient ID": patient_id, "NPI": npi, "CPT": cpt,
        "Modifier": "", "Units": 1, "ICD-10": random.choice(ICD_POOL),
        "Policy #": f"POL{random.randint(10000, 99999)}",
        "Date of Service": (today - timedelta(days=random.randint(370, 420))).isoformat(),
        "POS": "11", "Billed Amount": f"${billed:.2f}", "Allowed Amount": "",
        "Copay": 20, "Deductible": 0, "Coinsurance %": 20,
    })

# ---- intentional, varied errors (realistic sized batch) ----
def err_row(**over):
    claim_id, patient_id = next_ids()
    cpt, base_amt, _ = random.choice(CPT_POOL)
    base = {
        "Claim ID": claim_id, "Patient ID": patient_id, "NPI": random.choice(PROVIDERS),
        "CPT": cpt, "Modifier": "", "Units": 1, "ICD-10": random.choice(ICD_POOL),
        "Policy #": f"POL{random.randint(10000, 99999)}",
        "Date of Service": (today - timedelta(days=random.randint(0, 20))).isoformat(),
        "POS": "11", "Billed Amount": f"${base_amt:.2f}", "Allowed Amount": "",
        "Copay": 20, "Deductible": 0, "Coinsurance %": 20,
    }
    base.update(over)
    return base

rows.append(err_row(NPI="1234567890"))                       # bad check digit
rows.append(err_row(CPT="ABC12"))                             # bad CPT format
rows.append(err_row(**{"ICD-10": "E11..9"}))                  # bad ICD format
rows.append(err_row(Modifier="XYZ"))                          # bad modifier
rows.append(err_row(Units=0))                                 # invalid units
rows.append(err_row(**{"Policy #": ""}))                      # missing policy
rows.append(err_row(**{"Date of Service": (today + timedelta(days=10)).isoformat()}))  # future DOS
rows.append(err_row(**{"Billed Amount": "-$40.00"}))          # negative amount

dup_source = err_row()
rows.append(dup_source)
rows.append(dict(dup_source, **{"Claim ID": f"CLM{cid:04d}"}))
cid += 1

random.shuffle(rows)

path = os.path.join(OUTDIR, "Claims_Sample.csv")
fieldnames = ["Claim ID", "Patient ID", "NPI", "CPT", "Modifier", "Units", "ICD-10",
              "Policy #", "Date of Service", "POS", "Billed Amount", "Allowed Amount",
              "Copay", "Deductible", "Coinsurance %"]
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print("wrote", path, "rows:", len(rows))
