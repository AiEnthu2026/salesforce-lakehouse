import csv, os, random
from datetime import date, timedelta, datetime
from faker import Faker

SEED = 42
N_ACCOUNTS, N_CONTACTS, N_CASES, N_USAGE = 300, 500, 600, 3000
N_CONTRACTED, N_RENEWALS = 270, 5

random.seed(SEED)
Faker.seed(SEED)
fake = Faker("en_AU")

CITIES = [("Sydney", "New South Wales"), ("Melbourne", "Victoria"),
          ("Brisbane", "Queensland"), ("Perth", "Western Australia"),
          ("Adelaide", "South Australia"), ("Canberra", "Australian Capital Territory"),
          ("Hobart", "Tasmania")]
INDUSTRIES = ["Banking", "Retail", "Healthcare", "Education", "Energy", "Transportation", "Technology"]
SUBJECTS = ["Login issue", "Invoice query", "Service outage", "Billing dispute",
            "Feature request", "Data export problem"]
SERVICES = ["storage", "compute", "support", "licensing"]
BANKS = ["Commonwealth Bank", "Westpac", "NAB", "ANZ", "Macquarie Bank", "ING Australia"]
TIERS = {"Bronze" : 500, "Silver" : 1500, "Gold" : 4000, "Platinum" : 9000}

def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


refs = [f"CUST-{i:05d}" for i in range(1, N_ACCOUNTS + 1)]

accounts = []
for ref in refs:
    city, state = random.choice(CITIES)
    accounts.append({"Name": fake.company(), "Customer_Ref__c": ref,
                     "Industry": random.choice(INDUSTRIES),
                     "BillingCity": city, "BillingState": state, "BillingCountry": "Australia",
                     "Phone": fake.phone_number()})

contacts = [{"FirstName": fake.first_name(), "LastName": fake.last_name(),
             "Email": fake.email(), "Phone": fake.phone_number(),
             "Account.Customer_Ref__c": random.choice(refs)} for _ in range(N_CONTACTS)]

cases = [{"Subject": random.choice(SUBJECTS),
          "Status": random.choice(["New", "Working", "Escalated", "Closed"]),
          "Priority": random.choice(["High", "Medium", "Low"]),
          "Origin": random.choice(["Phone", "Email", "Web"]),
          "Account.Customer_Ref__c": random.choice(refs)} for _ in range(N_CASES)]

today = date(2026, 9, 29)
usage = [{"usage_id": f"U{i:06d}",
          "customer_ref": random.choice(refs),
          "usage_date": (today - timedelta(days=random.randint(0, 89))).isoformat(),
          "service": random.choice(SERVICES),
          "units": random.randint(1, 500),
          "amount_aud": round(random.uniform(5, 2500), 2),
          "payment_bank": random.choice(BANKS)} for i in range(1, N_USAGE + 1)]

tier_names = list(TIERS)
contracted = random.sample(refs, N_CONTRACTED)
renewals = set(random.sample(contracted, N_RENEWALS))
MODIFIED_AT = "2026-09-29T00:00:00"

contracts = []
contract_no = 0

def contract_row(ref, tier, start):
    global contract_no
    contract_no += 1
    return {"contract_id": f"K{contract_no:06d}",
            "customer_ref": ref,
            "contract_tier": tier,
            "committed_monthly_aud": round(TIERS[tier] * random.uniform(0.9, 1.1), 2),
            "contract_start": start.isoformat(),
            "contract_end": (start + timedelta(days=365)).isoformat(),
            "modified_at": MODIFIED_AT}

for ref in contracted:
    if ref in renewals:
        i = random.randrange(len(tier_names) - 1)
        old_start = today - timedelta(days=random.randint(450, 500))
        new_start = old_start + timedelta(days=366)
        contracts.append(contract_row(ref, tier_names[i], old_start))
        contracts.append(contract_row(ref, tier_names[i + 1], new_start))
    else:
        start = today - timedelta(days=random.randint(30, 330))
        contracts.append(contract_row(ref, random.choice(tier_names), start))

write("data/salesforce/accounts.csv", accounts)
write("data/salesforce/contacts.csv", contacts)
write("data/salesforce/cases.csv", cases)
write("data/blob/usage_20260929.csv", usage)
write("data/azure_sql/account_contracts.csv", contracts)
print("done")