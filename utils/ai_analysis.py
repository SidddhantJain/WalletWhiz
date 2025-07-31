def analyze_expenses(transactions, query):
    # Stub: Use NLP to parse query and filter transactions
    # Example: "How much did I spend on travel in June?"
    # Return dummy result for now
    return "Spent ₹1200 on travel in June."

def get_payment_method_stats(transactions):
    # Example: Most used payment method
    methods = {}
    for t in transactions:
        method = t.get("payment_method", "Unknown")
        methods[method] = methods.get(method, 0) + 1
    return max(methods, key=methods.get)
