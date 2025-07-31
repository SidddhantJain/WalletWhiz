from models.lending import LendingManager, LendingRecord

class LendingController:
    def __init__(self):
        self.manager = LendingManager()

    def add_lending(self, amount, person, reason, due_date):
        record = LendingRecord(amount, person, reason, due_date)
        self.manager.add_record(record)

    def mark_paid(self, index):
        self.manager.records[index].paid = True

    def get_summary(self):
        owed, paid = self.manager.get_balance()
        return f"You owe {owed}, Paid: {paid}"
