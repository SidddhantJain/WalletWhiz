def filter_by_tag(transactions, tag):
    return [t for t in transactions if tag in t.get("tags", [])]
