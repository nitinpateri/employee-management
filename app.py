import os

import requests
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
TABLE_URL = f"{SUPABASE_URL}/rest/v1/employees"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
FIELDS = ["name", "email", "department", "position", "salary", "hire_date"]


def form_data():
    data = {f: (request.form.get(f) or "").strip() or None for f in FIELDS}
    return data


def api_error(resp):
    try:
        return resp.json().get("message", resp.text)
    except Exception:
        return resp.text


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    params = {"select": "*", "order": "id.desc"}
    if q:
        params["or"] = f"(name.ilike.*{q}*,email.ilike.*{q}*,department.ilike.*{q}*)"
    resp = requests.get(TABLE_URL, headers=HEADERS, params=params, timeout=10)
    if not resp.ok:
        flash(f"Database error: {api_error(resp)}", "error")
        employees = []
    else:
        employees = resp.json()
    return render_template("index.html", employees=employees, q=q)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        resp = requests.post(TABLE_URL, headers=HEADERS, json=form_data(), timeout=10)
        if resp.ok:
            flash("Employee added.", "success")
            return redirect(url_for("index"))
        flash(f"Could not add employee: {api_error(resp)}", "error")
    return render_template("form.html", employee=None)


@app.route("/edit/<int:emp_id>", methods=["GET", "POST"])
def edit(emp_id):
    if request.method == "POST":
        resp = requests.patch(
            TABLE_URL, headers=HEADERS, params={"id": f"eq.{emp_id}"},
            json=form_data(), timeout=10,
        )
        if resp.ok:
            flash("Employee updated.", "success")
            return redirect(url_for("index"))
        flash(f"Could not update employee: {api_error(resp)}", "error")
    resp = requests.get(
        TABLE_URL, headers=HEADERS, params={"id": f"eq.{emp_id}", "select": "*"}, timeout=10
    )
    rows = resp.json() if resp.ok else []
    if not rows:
        flash("Employee not found.", "error")
        return redirect(url_for("index"))
    return render_template("form.html", employee=rows[0])


@app.route("/delete/<int:emp_id>", methods=["POST"])
def delete(emp_id):
    resp = requests.delete(TABLE_URL, headers=HEADERS, params={"id": f"eq.{emp_id}"}, timeout=10)
    if resp.ok:
        flash("Employee deleted.", "success")
    else:
        flash(f"Could not delete employee: {api_error(resp)}", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
