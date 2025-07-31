def detect_recurring(transactions):
    # Stub: Find transactions with similar amount/description monthly
    recurring = []
    for t in transactions:
        # Add logic for frequency detection
        if "netflix" in t["notes"].lower():
            recurring.append(t)
    return recurring
