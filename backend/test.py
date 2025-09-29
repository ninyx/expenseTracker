import json
import urllib.request
from datetime import datetime
from uuid import UUID

BASE_URL = "http://127.0.0.1:8000"

def post(path, data):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get(path):
    url = f"{BASE_URL}{path}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())

if __name__ == "__main__":
    # Accounts
    acc1 = post("/accounts/", {"name": "BDO Bank", "type": "bank", "balance": 10000})
    acc2 = post("/accounts/", {"name": "BDO Bank", "type": "bank", "balance": 5000})
    acc3 = post("/accounts/", {"name": "GCash Wallet", "type": "e-wallet", "balance": 2000})

    # Categories
    cat1 = post("/categories/", {"name": "Food & Groceries"})
    cat2 = post("/categories/", {"name": "Rent"})

    # Transactions
    t1 = post("/transactions/", {
        "amount": 1500,
        "type": "expense",
        "account_id": acc1["id"],
        "category_id": cat1["id"],
        "note": "Grocery shopping at SM",
        "fee": 0,
        "date": datetime.now().isoformat()
    })

    t2 = post("/transactions/", {
        "amount": 8000,
        "type": "expense",
        "account_id": acc1["id"],
        "category_id": cat2["id"],
        "note": "September rent",
        "fee": 0,
        "date": datetime.now().isoformat()
    })

    t3 = post("/transactions/", {
        "amount": 1000,
        "type": "transfer",
        "account_id": acc1["id"],
        "target_account_id": acc3["id"],
        "note": "Send money to GCash",
        "fee": 10,
        "date": datetime.now().isoformat()
    })

    print("Accounts:", get("/accounts/"))
    print("Categories:", get("/categories/"))
    print("Transactions:", get("/transactions/"))
