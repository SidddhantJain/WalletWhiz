def spending_insights(transactions):
    insights = []
    # Example: Compare food spending month-to-month
    food = [t for t in transactions if t["category"] == "Food"]
    if food:
        insights.append(f"You spent {sum(t['amount'] for t in food)} on Food.")
    # Add more insights as needed
    return insights

def predict_expenses(transactions):
    # Dummy prediction: next month same as this month
    predictions = {}
    for cat in set(t["category"] for t in transactions):
        predictions[cat] = sum(t["amount"] for t in transactions if t["category"] == cat)
    return predictions
