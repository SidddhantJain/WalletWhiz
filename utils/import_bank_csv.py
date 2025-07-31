import csv

def import_bank_csv(filename):
    transactions = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append({
                "date": row.get("Date"),
                "type": row.get("Type"),
                "amount": float(row.get("Amount", 0)),
                "category": row.get("Category", "Other"),
                "notes": row.get("Notes", ""),
                "tags": row.get("Tags", "").split(",") if row.get("Tags") else []
            })
    return transactions
