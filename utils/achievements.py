def check_achievements(transactions):
    achievements = []
    savings = sum(t["amount"] for t in transactions if t["type"] == "Income") - \
              sum(t["amount"] for t in transactions if t["type"] == "Expense")
    if savings >= 5000:
        achievements.append("🏅 Saved ₹5000 in one month!")
    # Add more rules
    return achievements
