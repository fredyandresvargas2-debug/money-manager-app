from flask import Flask, render_template_string, request, redirect, url_for, session

import database

app = Flask(__name__)
app.secret_key = "money-manager-secret"


HTML = """
<!doctype html>
<html>
<head>
  <title>Money Manager</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 20px; }
    .container { max-width: 1200px; margin: auto; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.08); margin-bottom: 20px; }
    form { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    input, select, button { padding: 10px; border-radius: 6px; border: 1px solid #d0d7de; }
    button { background: #2563eb; color: white; border: none; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; }
    .summary { display: flex; gap: 15px; flex-wrap: wrap; }
    .box { background: #eef6ff; padding: 15px; border-radius: 8px; min-width: 180px; }
    a { color: #2563eb; text-decoration: none; }
    .nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="nav">
      <h2>Money Manager</h2>
      {% if session.get('user_id') %}
        <a href="/logout">Cerrar sesión</a>
      {% endif %}
    </div>

    {% if error %}
      <div class="card"><strong>Error:</strong> {{ error }}</div>
    {% endif %}

    {% if session.get('user_id') %}
      <div class="card">
        <h3>Resumen</h3>
        <div class="summary">
          <div class="box"><b>Ingresos</b><br>${{ summary.income_total }}</div>
          <div class="box"><b>Gastos</b><br>${{ summary.expense_total }}</div>
          <div class="box"><b>Balance</b><br>${{ summary.balance }}</div>
        </div>
      </div>

      <div class="card">
        <h3>Registrar transacción</h3>
        <form action="/transaction" method="post">
          <select name="type" required>
            <option value="income">Ingreso</option>
            <option value="expense">Gasto</option>
          </select>
          <input type="text" name="category" placeholder="Categoría" required>
          <input type="number" step="0.01" name="amount" placeholder="Monto" required>
          <input type="text" name="description" placeholder="Descripción">
          <button type="submit">Guardar</button>
        </form>
      </div>

      <div class="card">
        <h3>Nuevo presupuesto</h3>
        <form action="/budget" method="post">
          <input type="text" name="category" placeholder="Categoría" required>
          <input type="number" step="0.01" name="limit_amount" placeholder="Límite" required>
          <button type="submit">Guardar</button>
        </form>
      </div>

      <div class="card">
        <h3>Historial</h3>
        <table>
          <tr><th>Tipo</th><th>Categoría</th><th>Monto</th><th>Descripción</th><th>Fecha</th></tr>
          {% for t in transactions %}
          <tr>
            <td>{{ t.type }}</td>
            <td>{{ t.category }}</td>
            <td>${{ '%.2f' % t.amount }}</td>
            <td>{{ t.description or '-' }}</td>
            <td>{{ t.created_at }}</td>
          </tr>
          {% endfor %}
        </table>
      </div>

      <div class="card">
        <h3>Presupuestos</h3>
        <table>
          <tr><th>Categoría</th><th>Límite</th></tr>
          {% for b in budgets %}
          <tr><td>{{ b.category }}</td><td>${{ '%.2f' % b.limit_amount }}</td></tr>
          {% endfor %}
        </table>
      </div>

      <div class="card">
        <h3>Gastos por categoría</h3>
        <table>
          <tr><th>Categoría</th><th>Total</th></tr>
          {% for e in categories %}
          <tr><td>{{ e.category }}</td><td>${{ '%.2f' % e.total }}</td></tr>
          {% endfor %}
        </table>
      </div>
    {% else %}
      <div class="card">
        <h3>Iniciar sesión</h3>
        <form action="/login" method="post">
          <input type="text" name="username" placeholder="Usuario" required>
          <input type="password" name="password" placeholder="Contraseña" required>
          <button type="submit">Entrar</button>
        </form>

        <h3>Registrarse</h3>
        <form action="/register" method="post">
          <input type="text" name="username" placeholder="Usuario" required>
          <input type="password" name="password" placeholder="Contraseña" required>
          <button type="submit">Crear cuenta</button>
        </form>
      </div>
    {% endif %}
  </div>
</body>
</html>
"""


def get_dashboard_context():
    user_id = session.get("user_id")
    if not user_id:
        return {"summary": {"income_total": 0, "expense_total": 0, "balance": 0}, "transactions": [], "budgets": [], "categories": []}

    summary = database.get_summary(user_id)
    return {
        "summary": summary,
        "transactions": database.get_transactions(user_id),
        "budgets": database.get_budgets(user_id),
        "categories": database.get_expenses_by_category(user_id),
    }


@app.route("/")
def index():
    context = get_dashboard_context()
    return render_template_string(HTML, **context, error=None)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    user = database.login_user(username, password)
    if not user:
        return render_template_string(HTML, error="Credenciales inválidas.", **get_dashboard_context())
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("index"))


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    try:
        database.register_user(username, password)
        return render_template_string(HTML, error="Usuario creado. Ahora inicia sesión.", **get_dashboard_context())
    except ValueError as exc:
        return render_template_string(HTML, error=str(exc), **get_dashboard_context())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/transaction", methods=["POST"])
def transaction():
    if "user_id" not in session:
        return redirect(url_for("index"))

    try:
        database.add_transaction(
            session["user_id"],
            request.form.get("type", "expense"),
            request.form.get("category", "otra").strip(),
            float(request.form.get("amount", 0)),
            request.form.get("description", "").strip(),
        )
    except ValueError as exc:
        return render_template_string(HTML, error=str(exc), **get_dashboard_context())
    return redirect(url_for("index"))


@app.route("/budget", methods=["POST"])
def budget():
    if "user_id" not in session:
        return redirect(url_for("index"))

    try:
        database.add_budget(
            session["user_id"],
            request.form.get("category", "").strip(),
            float(request.form.get("limit_amount", 0)),
        )
    except ValueError as exc:
        return render_template_string(HTML, error=str(exc), **get_dashboard_context())
    return redirect(url_for("index"))


if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)
