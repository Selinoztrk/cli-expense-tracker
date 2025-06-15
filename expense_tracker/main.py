import sqlite3
from datetime import datetime

class Expense:
    def __init__(self, date, description, amount, category):
        self.date = date
        self.description = description
        self.amount = amount
        self.category = category


class ExpenseTracker:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.budget_limit = None

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                amount REAL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        self.conn.commit()

    def get_or_create_category_id(self, category_name):
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            self.conn.commit()
            return self.cursor.lastrowid

    def add_expense(self, expense):
        category_id = self.get_or_create_category_id(expense.category)
        self.cursor.execute("INSERT INTO expenses (date, description, amount, category_id) VALUES (?, ?, ?, ?)",
                            (expense.date, expense.description, expense.amount, category_id))
        self.conn.commit()
        self.check_budget_limit()

    def remove_expense(self, index):
        expenses = self.get_all_expenses()
        if 0 <= index < len(expenses):
            expense_id = expenses[index][0]
            self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.conn.commit()
            print("Expense removed successfully.")
        else:
            print("Invalid expense index.")

    def get_all_expenses(self):
        self.cursor.execute("""
            SELECT e.id, e.date, e.description, e.amount, c.name
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            ORDER BY e.date DESC
        """)
        return self.cursor.fetchall()

    def view_expenses(self):
        expenses = self.get_all_expenses()
        if not expenses:
            print("No expenses found.")
        else:
            print("Expense List:")
            for i, expense in enumerate(expenses, start=1):
                print(f"{i}. Date: {expense[1]}, Description: {expense[2]}, Amount: ${expense[3]:.2f}, Category: {expense[4]}")

    def total_expenses(self):
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        total = self.cursor.fetchone()[0] or 0
        print(f"Total Expenses: ${total:.2f}")

    def expenses_by_category(self):
        self.cursor.execute("""
            SELECT c.name, SUM(e.amount)
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            GROUP BY e.category_id
        """)
        rows = self.cursor.fetchall()
        if not rows:
            print("No expenses found.")
        else:
            print("Expenses by Category:")
            for category, total in rows:
                print(f"{category}: ${total:.2f}")

    def filter_by_date_range(self, start_date_str, end_date_str):
        try:
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        self.cursor.execute("""
            SELECT e.date, e.description, e.amount, c.name
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE date BETWEEN ? AND ?
            ORDER BY e.date
        """, (start_date_str, end_date_str))
        rows = self.cursor.fetchall()

        if not rows:
            print("No expenses found in this date range.")
        else:
            print(f"Expenses from {start_date_str} to {end_date_str}:")
            for i, expense in enumerate(rows, start=1):
                print(f"{i}. Date: {expense[0]}, Description: {expense[1]}, Amount: ${expense[2]:.2f}, Category: {expense[3]}")

    def search_by_description(self, keyword):
        self.cursor.execute("""
            SELECT e.date, e.description, e.amount, c.name
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE description LIKE ?
        """, (f"%{keyword}%",))
        results = self.cursor.fetchall()

        if not results:
            print(f"No expenses found with description containing '{keyword}'.")
        else:
            print(f"Expenses matching '{keyword}':")
            for i, expense in enumerate(results, start=1):
                print(f"{i}. Date: {expense[0]}, Description: {expense[1]}, Amount: ${expense[2]:.2f}, Category: {expense[3]}")

    def set_budget_limit(self, limit):
        self.budget_limit = limit
        print(f"Monthly budget set to ${limit:.2f}")

    def check_budget_limit(self):
        if self.budget_limit is None:
            return

        current_month = datetime.now().strftime("%Y-%m")
        self.cursor.execute("SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = ?", (current_month,))
        total = self.cursor.fetchone()[0] or 0

        if total > self.budget_limit:
            print(f"⚠️ Budget exceeded! You've spent ${total:.2f} this month (limit: ${self.budget_limit:.2f})")

    def exit_program(self):
        self.conn.close()
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
            try:
                amount = float(input("Enter the amount: "))
            except ValueError:
                print("Invalid amount.")
                continue
            category = input("Enter the category: ")
            expense = Expense(date, description, amount, category)
            tracker.add_expense(expense)
            print("Expense added successfully.")
        elif choice == "2":
            index = int(input("Enter the expense index to remove: ")) - 1
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
