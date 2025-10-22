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
# Category seeding
# ---------------------------

def random_category():
    """Generate a dummy category dictionary."""
    names = ["Food", "Transportation", "Entertainment", "Salary", "Shopping", "Utilities", "Health", "Education"]
    transaction_type = random.choice(["income", "expense"])
    return {
        "name": f"{random.choice(names)} {transaction_type.capitalize()}",
        "transaction_type": transaction_type,
        "budgeted_amount": round(random.uniform(100, 2000), 2),
        "frequency": random.choice(["monthly", "weekly", "yearly", "one-time"])
    }

def seed_categories(n=5):
    print(f"🚀 Seeding {n} dummy categories...")
    success = 0
    fail = 0
    created_categories = []

    for _ in range(n):
        cat = random_category()
        try:
            res = requests.post(f"{API_BASE}/categories/", json=cat)
            if res.status_code in (200, 201):
                print(f"✅ Created category: {cat['name']}")
                success += 1
                created_categories.append(res.json().get("uid") or res.json().get("id"))
            else:
                print(f"⚠️ Failed ({res.status_code}): {res.text}")
                fail += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            fail += 1

    print(f"\nCategories done! ✅ {success} succeeded, ❌ {fail} failed.\n")
    return created_categories


# ---------------------------
# Transaction seeding
# ---------------------------

def random_transaction(account_uids, category_uids):
    """Generate a dummy transaction dictionary compatible with the API."""
    types = ["income", "expense", "reimburse", "transfer"]
    ttype = random.choice(types)
    amount = round(random.uniform(100, 5000), 2)
    desc = f"Dummy {ttype} transaction"

    acct_from = random.choice(account_uids) if account_uids else "acct-cash"
    acct_to = random.choice(account_uids) if account_uids else "acct-wallet"
    category_uid = random.choice(category_uids) if category_uids else None

    if ttype in ["income", "expense"]:
        return {
            "type": ttype,
            "account_uid": acct_from,
            "category_uid": category_uid,
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

def seed_transactions(n=10, account_uids=None, category_uids=None):
    print(f"🚀 Seeding {n} dummy transactions...")
    success = 0
    fail = 0

    for _ in range(n):
        tx = random_transaction(account_uids, category_uids)
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

    # 2️⃣ Seed categories and get their UIDs
    category_uids = seed_categories(5)

    # 3️⃣ Use these accounts and categories to seed transactions
    seed_transactions(10, account_uids, category_uids)
