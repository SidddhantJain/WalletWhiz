class SavingsGoal:
    def __init__(self, name, target_amount, current_amount=0):
        self.name = name
        self.target_amount = target_amount
        self.current_amount = current_amount

class GoalManager:
    def __init__(self):
        self.goals = []

    def add_goal(self, goal):
        self.goals.append(goal)

    def update_progress(self, goal_index, amount):
        self.goals[goal_index].current_amount += amount
