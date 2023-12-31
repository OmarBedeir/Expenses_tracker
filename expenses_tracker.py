import tkinter as tk
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
import requests
from tkinter import messagebox

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")  # Set initial window size

        # Variables to store user inputs
        self.amount_var = tk.DoubleVar()
        self.category_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.payment_method_var = tk.StringVar()
        self.currency_var = tk.StringVar(value="USD")  # Default currency is USD
        self.image_path_var = tk.StringVar()  # Variable to store the image path

        # Fixer API key
        self.api_key = "xczqFWwhlZIuKNhVXK2KD2ol8H55Vujw"

        # GUI components
        self.setup_gui()

    def setup_gui(self):
        # Create a style to use for ttk widgets
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 12), rowheight=25)  # Adjust font and row height

        # Set colors and fonts for labels
        label_font = ('Arial', 12, 'bold')
        label_color = '#4CAF50'  # Green color
        bg_color = '#E1F5FE'  # Light blue background color

        # Labels and Entry Widgets
        tk.Label(self.root, text="Amount:", font=label_font, fg=label_color, bg=bg_color).grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.amount_var, font=('Arial', 12)).grid(row=0, column=1)

        tk.Label(self.root, text="Category:", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=0)
        categories = ["Food", "Transportation", "Utilities", "Entertainment"]
        category_dropdown = ttk.Combobox(self.root, textvariable=self.category_var, values=categories, font=('Arial', 12))
        category_dropdown.grid(row=1, column=1)

        tk.Label(self.root, text="Date:", font=label_font, fg=label_color, bg=bg_color).grid(row=2, column=0)
        date_picker = DateEntry(self.root, textvariable=self.date_var, date_pattern="yyyy-mm-dd", font=('Arial', 12))
        date_picker.grid(row=2, column=1)

        tk.Label(self.root, text="Payment Method:", font=label_font, fg=label_color, bg=bg_color).grid(row=3, column=0)
        payment_methods = ["Cash", "Credit Card", "Debit Card"]
        payment_dropdown = ttk.Combobox(self.root, textvariable=self.payment_method_var, values=payment_methods, font=('Arial', 12))
        payment_dropdown.grid(row=3, column=1)

        tk.Label(self.root, text="Currency:", font=label_font, fg=label_color, bg=bg_color).grid(row=4, column=0)
        currencies = ["USD", "EUR", "GBP", "JPY"]
        currency_dropdown = ttk.Combobox(self.root, textvariable=self.currency_var, values=currencies, font=('Arial', 12))
        currency_dropdown.grid(row=4, column=1)

        # Button with Hover Animation
        add_button = tk.Button(self.root, text="Add Expense", command=self.add_expense, font=('Arial', 14), bg='#4CAF50', fg='white')
        add_button.grid(row=5, column=0, columnspan=2, pady=10)
        add_button.bind("<Enter>", lambda event: add_button.config(bg='#45A049'))  # Hover color
        add_button.bind("<Leave>", lambda event: add_button.config(bg='#4CAF50'))  # Normal color

        # Button to attach image
        attach_image_button = tk.Button(self.root, text="Attach Image", command=self.attach_image, font=('Arial', 14), bg='#FF9800', fg='white')
        attach_image_button.grid(row=6, column=0, columnspan=2, pady=10)

        # App Information Button
        info_button = tk.Button(self.root, text="App Information", command=self.show_app_information, font=('Arial', 14), bg='#2196F3', fg='white')
        info_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Quit Button
        quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy, font=('Arial', 14), bg='#FF5722', fg='white')
        quit_button.grid(row=8, column=0, columnspan=2, pady=10)

        # Exit Button
        exit_button = tk.Button(self.root, text="Exit", command=self.exit_application, font=('Arial', 14), bg='#FF5722', fg='white')
        exit_button.grid(row=9, column=0, columnspan=2, pady=10)

        # Table for displaying expenses
        columns = ["Original Amount", "Category", "Date", "Payment Method", "Original Currency", "Converted Amount (USD)", "Image Path"]
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            # Tag configuration for the "Converted Amount (USD)" column
            if col == "Converted Amount (USD)":
                self.tree.tag_configure(col, background='#FFC107')  # Use your preferred color here
        self.tree.grid(row=10, column=0, columnspan=2, pady=10)

        # Total expenses row (inside the table)
        self.total_row_id = self.tree.insert("", "end", values=("Total Expenses (USD):", "", "", "", "", "", ""), tags=('total_row',))

        # Configure a tag for the 'total_row' with a background color
        self.tree.tag_configure('total_row', background='#FFEB3B')

        # Set up a trace on the treeview items to recalculate total when items change
        self.tree.bind("<<TreeviewSelect>>", self.update_total_expenses)

    def attach_image(self):
        # Open a file dialog to select an image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])

        # Update the image path variable
        self.image_path_var.set(file_path)

    def add_expense(self):
        # Get user inputs, including the image path
        amount = self.amount_var.get()
        category = self.category_var.get()
        date_str = self.date_var.get()
        payment_method = self.payment_method_var.get()
        original_currency = self.currency_var.get()
        image_path = self.image_path_var.get()

        # Convert amount to USD using Fixer API
        converted_amount = self.convert_to_usd(amount, original_currency)

        # Update table with the converted amount and image path
        item_id = self.tree.insert("", "end", values=(amount, category, date_str, payment_method, original_currency, converted_amount, image_path))

        # Calculate and update total expenses in USD
        self.update_total_expenses(item_id)

        # Display success message
        messagebox.showinfo("Expense Added", "Expense successfully added!")

        # Clear input fields and image path
        self.amount_var.set(0.0)
        self.category_var.set("")
        self.date_var.set("")
        self.payment_method_var.set("")
        self.currency_var.set("USD")
        self.image_path_var.set("")

    def update_total_expenses(self, item_id):
        # Calculate and update total expenses in USD
        total_expenses_usd = sum(float(self.tree.item(item, 'values')[5]) for item in self.tree.get_children() if item != self.total_row_id)
        self.tree.item(self.total_row_id, values=("Total Expenses (USD):", "", "", "", "", "", f"${total_expenses_usd:.2f}"))

    def convert_to_usd(self, amount, from_currency):
        # Call Fixer API for currency conversion
        to_currency = "USD"

        url = f"https://api.apilayer.com/fixer/convert?to={to_currency}&from={from_currency}&amount={amount}"

        headers = {
            "apikey": self.api_key
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["result"]
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return amount  # Return original amount if conversion fails

    def show_app_information(self):
        # Create a new window for App Information
        app_info_window = tk.Toplevel(self.root)
        app_info_window.title("App Information")
        app_info_window.geometry("400x300")

        # Add widgets and content for the App Information window
        info_label = tk.Label(app_info_window, text="Expense Tracker App Information", font=('Arial', 14, 'bold'))
        info_label.pack(pady=10)

        app_description = (
            "Welcome to the Expense Tracker app!\n\n"
            "This app allows you to keep track of your expenses by entering details such as the amount, category, date, "
            "payment method, and currency of each expense. The app will automatically convert the amount to USD using the "
            "Fixer API.\n\n"
            "To use the app:\n"
            "1. Enter the expense details in the input fields.\n"
            "2. Click on the 'Add Expense' button to add the expense to the table.\n"
            "3. View your expenses in the table, including the converted amount in USD.\n"
            "4. The 'Total Expenses' row at the bottom of the table shows the sum of all expenses in USD.\n\n"
            "Feel free to explore the app and manage your expenses efficiently!\n\n"
            "Copyright © 2023 by Omar Bedeir"
        )

        app_info_text = tk.Text(app_info_window, wrap=tk.WORD, font=('Arial', 12))
        app_info_text.insert(tk.END, app_description)
        app_info_text.pack(pady=10)

        #   button to close the App Information window
        close_button = tk.Button(app_info_window, text="Close", command=app_info_window.destroy, font=('Arial', 12), bg='#FF5722', fg='white')
        close_button.pack()

    def exit_application(self):
        # Display confirmation message before exiting
        user_response = messagebox.askyesno("Exit Application", "Are you sure you want to exit?")
        if user_response:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
