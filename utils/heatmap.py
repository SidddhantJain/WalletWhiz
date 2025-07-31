def generate_heatmap(transactions):
    # Return a dict: {date: color}
    heatmap = {}
    for t in transactions:
        color = "#F44336" if t["type"] == "Expense" else "#4CAF50"
        heatmap[t["date"]] = color
    return heatmap

def get_daily_spending(transactions):
    daily = {}
    for t in transactions:
        date = t["date"]
        daily.setdefault(date, 0)
        if t["type"] == "Expense":
            daily[date] += t["amount"]
    return daily

def get_heat_color(amount):
    # Simple color scale: green < yellow < orange < red
    if amount == 0:
        return "#e0e0e0"
    elif amount < 500:
        return "#4CAF50"
    elif amount < 2000:
        return "#FFEB3B"
    elif amount < 5000:
        return "#FF9800"
    else:
        return "#F44336"
