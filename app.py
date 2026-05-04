import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = "recepten.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            steps TEXT NOT NULL DEFAULT '',
            servings INTEGER NOT NULL DEFAULT 2,
            cook_time TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL REFERENCES recipe(id) ON DELETE CASCADE,
            item TEXT NOT NULL,
            amount REAL,
            unit TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0
        );
    """)
    # migratie voor bestaande DB
    for col, definition, table in [
        ("cook_time", "TEXT", "recipe"),
        ("tags", "TEXT", "recipe"),
        ("sort_order", "INTEGER NOT NULL DEFAULT 0", "ingredient"),
    ]:
        try:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # kolom bestaat al
    db.commit()
    db.close()


# --- Routes ---

@app.route("/")
def index():
    db = get_db()
    recipes = db.execute("SELECT * FROM recipe ORDER BY updated_at DESC").fetchall()
    return render_template("index.html", recipes=recipes)


@app.route("/recipes/new", methods=["GET", "POST"])
def new_recipe():
    if request.method == "POST":
        return _save_recipe(None)
    return render_template("edit.html", recipe=None, ingredients=[])


@app.route("/recipes/<int:id>")
def view_recipe(id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipe WHERE id = ?", [id]).fetchone()
    if not recipe:
        return "Recept niet gevonden", 404
    ingredients = db.execute("SELECT * FROM ingredient WHERE recipe_id = ? ORDER BY sort_order", [id]).fetchall()
    return render_template("view.html", recipe=recipe, ingredients=ingredients)


@app.route("/recipes/<int:id>/edit", methods=["GET", "POST"])
def edit_recipe(id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipe WHERE id = ?", [id]).fetchone()
    if not recipe:
        return "Recept niet gevonden", 404
    if request.method == "POST":
        return _save_recipe(id)
    ingredients = db.execute("SELECT * FROM ingredient WHERE recipe_id = ? ORDER BY sort_order", [id]).fetchall()
    return render_template("edit.html", recipe=recipe, ingredients=ingredients)


@app.route("/recipes/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
    db = get_db()
    db.execute("DELETE FROM recipe WHERE id = ?", [id])
    db.commit()
    return redirect(url_for("index"))


@app.route("/recipes/<int:id>/cook")
def cook(id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipe WHERE id = ?", [id]).fetchone()
    if not recipe:
        return "Recept niet gevonden", 404
    ingredients = db.execute("SELECT * FROM ingredient WHERE recipe_id = ? ORDER BY sort_order", [id]).fetchall()
    return render_template("cook.html", recipe=recipe, ingredients=ingredients)


# --- Helpers ---

def _save_recipe(id):
    db = get_db()
    f = request.form

    title = f.get("title", "").strip()
    steps = f.get("steps", "").strip()
    servings = int(f.get("servings") or 2)
    cook_time = f.get("cook_time", "").strip() or None
    tags = f.get("tags_value", "").strip() or None

    if id is None:
        cur = db.execute(
            "INSERT INTO recipe (title, steps, servings, cook_time, tags) VALUES (?, ?, ?, ?, ?)",
            [title, steps, servings, cook_time, tags],
        )
        id = cur.lastrowid
    else:
        db.execute(
            "UPDATE recipe SET title=?, steps=?, servings=?, cook_time=?, tags=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            [title, steps, servings, cook_time, tags, id],
        )
        db.execute("DELETE FROM ingredient WHERE recipe_id=?", [id])

    i = 0
    while True:
        item = f.get(f"item_{i}", "").strip()
        if not item:
            i += 1
            # stop na 3 lege rijen op rij (voor als iemand een gat heeft gelaten)
            if i > (last_filled + 3 if 'last_filled' in dir() else 3):
                break
            continue
        last_filled = i
        amount = f.get(f"amount_{i}", "").strip()
        unit = f.get(f"unit_{i}", "").strip()
        db.execute(
            "INSERT INTO ingredient (recipe_id, item, amount, unit, sort_order) VALUES (?, ?, ?, ?, ?)",
            [id, item, float(amount) if amount else None, unit or None, i],
        )
        i += 1

    db.commit()
    return redirect(url_for("view_recipe", id=id))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
