from datetime import datetime
import json
import os


class Expense:
    def __init__(self, date, description, amount, category):
        self.date = date
        self.description = description
        self.amount = amount
        self.category = category
    
    def to_dict(self):
        return {
            "date": self.date,
            "description": self.description,
            "amount": self.amount,
            "category": self.category
        }

    @staticmethod
    def from_dict(data):
        return Expense(
            data["date"],
            data["description"],
            data["amount"],
            data.get("category", "Uncategorized")
        )


class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.budget_limit = None
        self.load_from_file()
    
    def add_expense(self, expense):
        self.expenses.append(expense)
        self.check_budget_limit()
    
    def remove_expense(self, index):
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            print("Expense removed successfully.")
        else:
            print("Invalid expense index.")

    def view_expenses(self):
        if len(self.expenses) == 0:
            print("No expenses found.")
        else:
            print("Expense List: ")
            for i, expense in enumerate(self.expenses, start=1):
                print(f"{i}. Date: {expense.date}, Description: {expense.description}, Amount: ${expense.amount:.2f}, Category: {expense.category}")
    
    def total_expenses(self):
        total = sum(expense.amount for expense in self.expenses)
        print(f"Total Expenses: ${total:.2f}")
    
    def expenses_by_category(self):
        if not self.expenses:
            print("No expenses found.")
            return

        category_totals = {}
        for expense in self.expenses:
            category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount
        
        print("Expenses by Category:")
        for category, total in category_totals.items():
            print(f"{category}: ${total:.2f}")
    
    def filter_by_date_range(self, start_date_str, end_date_str):
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        filtered = [e for e in self.expenses if start_date <= datetime.strptime(e.date, "%Y-%m-%d") <= end_date]

        if not filtered:
            print("No expenses found in this date range.")
        else:
            print(f"Expenses from {start_date_str} to {end_date_str}:")
            for i, expense in enumerate(filtered, start=1):
                print(f"{i}. Date: {expense.date}, Description: {expense.description}, Amount: ${expense.amount:.2f}, Category: {expense.category}")
    
    def search_by_description(self, keyword):
        results = [e for e in self.expenses if keyword.lower() in e.description.lower()]
        
        if not results:
            print(f"No expenses found with description containing '{keyword}'.")
        else:
            print(f"Expenses matching '{keyword}':")
            for i, expense in enumerate(results, start=1):
                print(f"{i}. Date: {expense.date}, Description: {expense.description}, Amount: ${expense.amount:.2f}, Category: {expense.category}")
    
    def set_budget_limit(self, limit):
        self.budget_limit = limit
        print(f"Monthly budget set to ${limit:.2f}")
    
    def check_budget_limit(self):
        if self.budget_limit is None:
            return

        from datetime import datetime

        current_month = datetime.now().strftime("%Y-%m")
        monthly_total = 0

        for expense in self.expenses:
            if expense.date.startswith(current_month):  # YYYY-MM format
                monthly_total += expense.amount

        if monthly_total > self.budget_limit:
            print(f"⚠️ Budget exceeded! You've spent ${monthly_total:.2f} this month (limit: ${self.budget_limit:.2f})")
    
    def save_to_file(self, filename="expenses.json"):
        data = [expense.to_dict() for expense in self.expenses]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print("✅ Expenses saved to file.")

    def load_from_file(self, filename="expenses.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try:
                    data = json.load(f)
                    self.expenses = [Expense.from_dict(item) for item in data]
                    print(f"📂 Loaded {len(self.expenses)} expenses from file.")
                except json.JSONDecodeError:
                    print("⚠️ Could not read file, starting with empty list.")
                    self.expenses = []
        else:
            print("📁 No saved data found.")

    def exit_program(self):
        self.save_to_file()
        print("Goodbye!")


def main():
    tracker = ExpenseTracker()

    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add Expense")
        print("2. Remove Expense")
        print("3. View Expenses")
        print("4. Total Expenses")
        print("5. View Expenses by Category")
        print("6. Filter Expenses by Date Range")
        print("7. Search Expenses by Description")
        print("8. Set Monthly Budget Limit")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == "1":
            date = input("Enter the date (YYYY-MM-DD): ")
            description = input("Enter the description: ")
            amount = float(input("Enter the amount: "))
            category = input("Enter the category: ")
            expense = Expense(date, description, amount, category)
            tracker.add_expense(expense)
            print("Expense added successfully.")
        elif choice == "2":
            index = int(input("Enter the expense index to remove: ")) -1
            tracker.remove_expense(index)
        elif choice == "3":
            tracker.view_expenses()
        elif choice == "4":
            tracker.total_expenses()
        elif choice == "5":
            tracker.expenses_by_category()
        elif choice == "6":
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            tracker.filter_by_date_range(start_date, end_date)
        elif choice == "7":
            keyword = input("Enter keyword to search in descriptions: ")
            tracker.search_by_description(keyword)
        elif choice == "8":
            try:
                limit = float(input("Enter your monthly budget limit: "))
                tracker.set_budget_limit(limit)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "9":
            tracker.exit_program()
            break


if __name__ == "__main__":
    main()