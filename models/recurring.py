class RecurringPayment:
    def __init__(self, name, amount, due_date, category, active=True):
        self.name = name
        self.amount = amount
        self.due_date = due_date
        self.category = category
        self.active = active

class RecurringManager:
    def __init__(self):
        self.payments = []

    def add_payment(self, payment):
        self.payments.append(payment)

    def get_due_payments(self, today):
        return [p for p in self.payments if p.due_date == today and p.active]
