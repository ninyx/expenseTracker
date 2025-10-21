import requests
import random
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8000"  # adjust if needed


def random_date():
    """Generate a random date within the last 90 days."""
    start = datetime.now() - timedelta(days=90)
    end = datetime.now()
    random_dt = start + (end - start) * random.random()
    return random_dt.isoformat()  # ✅ convert to string


def random_transaction():
    """Generate a dummy transaction dictionary compatible with the API."""
    types = ["income", "expense", "reimburse", "transfer"]
    ttype = random.choice(types)
    amount = round(random.uniform(100, 5000), 2)
    desc = f"Dummy {ttype} transaction"

    # For non-transfer transactions
    if ttype in ["income", "expense"]:
        return {
            "type": ttype,
            "account_uid": "acct-cash",          # adjust with your actual test UIDs
            "category_uid": "cat-food",          # adjust
            "amount": amount,
            "description": desc,
            "date": random_date(),               # ✅ always a string
        }

    # For transfer transactions
    elif ttype == "transfer":
        return {
            "type": "transfer",
            "from_account_uid": "acct-bank",     # adjust
            "to_account_uid": "acct-wallet",     # adjust
            "amount": amount,
            "description": desc,
            "date": random_date(),               # ✅ always a string
        }

    elif ttype == "reimburse":
        return {
            "type": "reimburse",
            "account_uid": "acct-cash",          # adjust
            "expense_uid": "tx-expense123",      # adjust with an actual expense transaction UID
            "amount": amount,
            "description": desc,
            "date": random_date(),               # ✅ always a string
        }


def seed_transactions(n=10):
    print(f"🚀 Seeding {n} dummy transactions...")
    success = 0
    fail = 0

    for _ in range(n):
        tx = random_transaction()
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

    print(f"\nDone! ✅ {success} succeeded, ❌ {fail} failed.")


if __name__ == "__main__":
    seed_transactions(5)
