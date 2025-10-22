import requests
import random
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8000"  # adjust if needed

# ---------------------------
# Helper functions
# ---------------------------

def random_date():
    """Generate a random date within the last 90 days."""
    start = datetime.now() - timedelta(days=90)
    end = datetime.now()
    random_dt = start + (end - start) * random.random()
    return random_dt.isoformat()  # ✅ convert to string


# ---------------------------
# Account seeding
# ---------------------------

def random_account():
    """Generate a dummy account dictionary."""
    account_types = ["cash", "checking", "savings", "credit card", "loan", "mortgage", "investment", "retirement", "digital wallet"]
    name = f"Test {random.choice(account_types).capitalize()} Account"
    return {
        "name": name,
        "type": random.choice(account_types),
        "balance": round(random.uniform(1000, 10000), 2)
    }

def seed_accounts(n=3):
    print(f"🚀 Seeding {n} dummy accounts...")
    success = 0
    fail = 0
    created_accounts = []

    for _ in range(n):
        acct = random_account()
        try:
            res = requests.post(f"{API_BASE}/accounts/", json=acct)
            if res.status_code in (200, 201):
                print(f"✅ Created account: {acct['name']}")
                success += 1
                # store returned UID for linking to transactions
                created_accounts.append(res.json().get("uid") or res.json().get("id"))
            else:
                print(f"⚠️ Failed ({res.status_code}): {res.text}")
                fail += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            fail += 1

    print(f"\nAccounts done! ✅ {success} succeeded, ❌ {fail} failed.\n")
    return created_accounts


# ---------------------------
# Transaction seeding
# ---------------------------

def random_transaction(account_uids):
    """Generate a dummy transaction dictionary compatible with the API."""
    types = ["income", "expense", "reimburse", "transfer"]
    ttype = random.choice(types)
    amount = round(random.uniform(100, 5000), 2)
    desc = f"Dummy {ttype} transaction"

    # pick random accounts from the seeded ones
    acct_from = random.choice(account_uids) if account_uids else "acct-cash"
    acct_to = random.choice(account_uids) if account_uids else "acct-wallet"

    if ttype in ["income", "expense"]:
        return {
            "type": ttype,
            "account_uid": acct_from,
            "category_uid": "cat-food",  # adjust as needed
            "amount": amount,
            "description": desc,
            "date": random_date(),
        }
    elif ttype == "transfer":
        return {
            "type": "transfer",
            "from_account_uid": acct_from,
            "to_account_uid": acct_to,
            "amount": amount,
            "description": desc,
            "date": random_date(),
        }
    elif ttype == "reimburse":
        return {
            "type": "reimburse",
            "account_uid": acct_from,
            "expense_uid": "tx-expense123",  # adjust with a real expense UID
            "amount": amount,
            "description": desc,
            "date": random_date(),
        }


def seed_transactions(n=10, account_uids=None):
    print(f"🚀 Seeding {n} dummy transactions...")
    success = 0
    fail = 0

    for _ in range(n):
        tx = random_transaction(account_uids)
        try:
            res = requests.post(f"{API_BASE}/transactions/", json=tx)
            if res.status_code in (200, 201):
                print(f"✅ Created: {tx['type']} ({tx['amount']})")
                success += 1
            else:
                print(f"⚠️ Failed ({res.status_code}): {res.text}")
                fail += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            fail += 1

    print(f"\nTransactions done! ✅ {success} succeeded, ❌ {fail} failed.\n")


# ---------------------------
# Main script
# ---------------------------

if __name__ == "__main__":
    # 1️⃣ Seed accounts first and get their UIDs
    account_uids = seed_accounts(5)

    # 2️⃣ Use these accounts to seed transactions
    seed_transactions(10, account_uids)
