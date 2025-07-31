import csv

def import_bank_csv(filename, mapping_rules=None):
    transactions = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = row.get("Description", "")
            category = "Other"
            if mapping_rules:
                for key, value in mapping_rules.items():
                    if key.lower() in desc.lower():
                        category = value
                        break
            transactions.append({
                "date": row.get("Date"),
                "type": row.get("Type", "Expense"),
                "amount": float(row.get("Amount", 0)),
                "category": category,
                "notes": desc,
                "tags": []
            })
    return transactions
