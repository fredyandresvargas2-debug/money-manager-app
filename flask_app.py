import tkinter as tk
from tkinter import ttk, messagebox

import database


class MoneyManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Money Manager")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.current_user = None
        self.build_login_screen()

    def build_login_screen(self):
        self.clear_screen()
        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)

        ttk.Label(frame, text="Money Manager", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        ttk.Label(frame, text="Usuario:").grid(row=1, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, pady=5)

        buttons = ttk.Frame(frame)
        buttons.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(buttons, text="Iniciar sesión", command=self.login).pack(side="left", padx=5)
        ttk.Button(buttons, text="Registrarse", command=self.register).pack(side="left", padx=5)

    def build_dashboard(self):
        self.clear_screen()

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text=f"Usuario: {self.current_user['username']}", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right")

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(controls, text="Registrar ingreso", command=lambda: self.add_transaction("income")).pack(side="left", padx=5)
        ttk.Button(controls, text="Registrar gasto", command=lambda: self.add_transaction("expense")).pack(side="left", padx=5)
        ttk.Button(controls, text="Nuevo presupuesto", command=self.add_budget).pack(side="left", padx=5)
        ttk.Button(controls, text="Actualizar", command=self.refresh_dashboard).pack(side="left", padx=5)

        summary_frame = ttk.LabelFrame(self.root, text="Resumen", padding=10)
        summary_frame.pack(fill="x", padx=10, pady=5)

        self.summary_labels = {
            "income": tk.StringVar(),
            "expense": tk.StringVar(),
            "balance": tk.StringVar(),
        }

        ttk.Label(summary_frame, text="Ingresos:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(summary_frame, textvariable=self.summary_labels["income"]).grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(summary_frame, text="Gastos:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(summary_frame, textvariable=self.summary_labels["expense"]).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(summary_frame, text="Balance:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(summary_frame, textvariable=self.summary_labels["balance"]).grid(row=2, column=1, sticky="w", padx=5)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        transactions_tab = ttk.Frame(notebook)
        budgets_tab = ttk.Frame(notebook)
        categories_tab = ttk.Frame(notebook)

        notebook.add(transactions_tab, text="Transacciones")
        notebook.add(budgets_tab, text="Presupuestos")
        notebook.add(categories_tab, text="Gastos por categoría")

        self.transactions_tree = ttk.Treeview(transactions_tab, columns=("id", "type", "category", "amount", "description", "date"), show="headings")
        for col in ("id", "type", "category", "amount", "description", "date"):
            self.transactions_tree.heading(col, text=col.title())
            self.transactions_tree.column(col, width=140, anchor="center")
        self.transactions_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.budgets_tree = ttk.Treeview(budgets_tab, columns=("category", "limit"), show="headings")
        self.budgets_tree.heading("category", text="Categoría")
        self.budgets_tree.heading("limit", text="Límite")
        self.budgets_tree.column("category", width=220)
        self.budgets_tree.column("limit", width=160)
        self.budgets_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.categories_tree = ttk.Treeview(categories_tab, columns=("category", "total"), show="headings")
        self.categories_tree.heading("category", text="Categoría")
        self.categories_tree.heading("total", text="Total")
        self.categories_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.refresh_dashboard()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        user = database.login_user(username, password)
        if user:
            self.current_user = user
            self.build_dashboard()
        else:
            messagebox.showerror("Error", "Credenciales inválidas.")

    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        try:
            database.register_user(username, password)
            messagebox.showinfo("Registro", "Usuario creado correctamente.")
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def logout(self):
        self.current_user = None
        self.build_login_screen()

    def add_transaction(self, type_):
        if not self.current_user:
            return

        category = simple_input("Categoría", "Ej: comida, transporte, salario")
        if category is None:
            return

        amount = simple_float_input("Monto")
        if amount is None:
            return

        description = simple_input("Descripción", "Opcional")
        if description is None:
            description = ""

        try:
            database.add_transaction(self.current_user["id"], type_, category, amount, description)
            self.refresh_dashboard()
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def add_budget(self):
        if not self.current_user:
            return

        category = simple_input("Categoría del presupuesto", "Ej: comida")
        if category is None:
            return

        limit_amount = simple_float_input("Límite del presupuesto")
        if limit_amount is None:
            return

        try:
            database.add_budget(self.current_user["id"], category, limit_amount)
            self.refresh_dashboard()
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def refresh_dashboard(self):
        if not self.current_user:
            return

        summary = database.get_summary(self.current_user["id"])
        self.summary_labels["income"].set(f"${summary['income_total']:.2f}")
        self.summary_labels["expense"].set(f"${summary['expense_total']:.2f}")
        self.summary_labels["balance"].set(f"${summary['balance']:.2f}")

        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        for row in database.get_transactions(self.current_user["id"]):
            self.transactions_tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["type"],
                    row["category"],
                    f"{row['amount']:.2f}",
                    row["description"],
                    row["created_at"],
                ),
            )

        for item in self.budgets_tree.get_children():
            self.budgets_tree.delete(item)
        for row in database.get_budgets(self.current_user["id"]):
            self.budgets_tree.insert("", "end", values=(row["category"], f"{row['limit_amount']:.2f}"))

        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        for row in database.get_expenses_by_category(self.current_user["id"]):
            self.categories_tree.insert("", "end", values=(row["category"], f"{row['total']:.2f}"))


def simple_input(title, default=""):
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.transient()
    dialog.grab_set()

    value = tk.StringVar(value=default)
    ttk.Label(dialog, text=f"{title}:").pack(padx=10, pady=(10, 5))
    ttk.Entry(dialog, textvariable=value, width=35).pack(padx=10, pady=(0, 10))

    result = {"value": None}

    def ok():
        result["value"] = value.get().strip()
        dialog.destroy()

    ttk.Button(dialog, text="Aceptar", command=ok).pack(pady=(0, 10))
    dialog.wait_window()
    return result["value"]


def simple_float_input(title):
    value = simple_input(title)
    if value is None:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        messagebox.showerror("Error", "Ingrese un número válido.")
        return None


if __name__ == "__main__":
    database.init_db()
    root = tk.Tk()
    app = MoneyManagerApp(root)
    root.mainloop()
