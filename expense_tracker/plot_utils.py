import matplotlib.pyplot as plt

def plot_expense_by_category(cursor):
    cursor.execute("""
        SELECT c.name, SUM(e.amount) 
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        GROUP BY c.name
    """)
    data = cursor.fetchall()
    if not data:
        print("No expense data to plot.")
        return

    labels, amounts = zip(*data)
    plt.figure(figsize=(8, 8))
    plt.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Expenses by Category')
    plt.axis('equal')
    plt.show()

def plot_monthly_expenses(cursor):
    cursor.execute('''
        SELECT strftime('%Y-%m', date) AS month, SUM(amount)
        FROM expenses
        GROUP BY month
        ORDER BY month
    ''')

    months = []
    totals = []

    for row in cursor.fetchall():
        month, total = row
        if month is not None and total is not None:
            months.append(month)
            totals.append(total)

    if not months:
        print("No expenses to plot.")
        return

    plt.bar(months, totals, color='skyblue')
    plt.title("Monthly Expenses")
    plt.xlabel("Month")
    plt.ylabel("Total Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
