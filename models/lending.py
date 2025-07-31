class LendingRecord:
    def __init__(self, amount, person, reason, due_date, paid=False):
        self.amount = amount
        self.person = person
        self.reason = reason
        self.due_date = due_date
        self.paid = paid

class LendingManager:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def get_balance(self):
        owed = sum(r.amount for r in self.records if not r.paid)
        paid = sum(r.amount for r in self.records if r.paid)
        return owed, paid

    def export_csv(self, filename):
        import csv
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Amount", "Person", "Reason", "Due Date", "Paid"])
            for r in self.records:
                writer.writerow([r.amount, r.person, r.reason, r.due_date, r.paid])
