from app import crud, database, schemas
from sqlalchemy.orm import Session

def print_db_contents(db: Session):
    # Fetch all data
    accounts = crud.get_accounts(db)
    categories = crud.get_categories(db)
    MonthlyBudgets = crud.get_budgets(db)
    transactions = crud.get_transactions(db)

    # Print Accounts
    print("\nAccounts:")
    for acc in accounts:
        print(f"UID: {acc.uid}, Name: {acc.name}, Type: {acc.type}, Balance: {acc.balance}")

    # Print Categories
    print("\nCategories:")
    for cat in categories:
        print(f"ID: {cat.id}, Name: {cat.name}")

    # Print MonthlyBudgets
    print("\nMonthlyBudgets:")
    for b in MonthlyBudgets:
        print(f"ID: {b.id}, Category: {b.category_id}, Month: {b.month}, Amount: {b.amount}")

    # Print Transactions
    print("\nTransactions:")
    for t in transactions:
        print(
            f"ID: {t.id}, Amount: {t.amount}, Type: {t.type}, "
            f"Account: {t.account_id}, Target Account: {getattr(t, 'target_account_id', None)}, "
            f"Category: {getattr(t, 'category_id', None)}, Fee: {t.fee}, Note: {t.note}, Date: {t.date}"
        )


if __name__ == "__main__":
    db = next(database.get_db())
    print_db_contents(db)
