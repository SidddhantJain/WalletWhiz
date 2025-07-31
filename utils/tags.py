def extract_tags(text):
    # Extract tags from notes or description (e.g., "#food #urgent")
    return [word[1:] for word in text.split() if word.startswith("#")]

def suggest_tags(transactions, prefix):
    # Suggest tags based on prefix and past entries
    tags = set()
    for t in transactions:
        for tag in t.get("tags", []):
            if tag.startswith(prefix):
                tags.add(tag)
    return list(tags)

def filter_transactions_by_tag(transactions, tag):
    return [t for t in transactions if tag in t.get("tags", [])]
