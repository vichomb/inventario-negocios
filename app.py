import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def conectar():
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla():
    conn = conectar()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

crear_tabla()

@app.route("/")
def inicio():

    conn = conectar()
    productos = conn.execute(
        "SELECT * FROM productos ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "index.html",
        productos=productos
    )

@app.route("/agregar", methods=["POST"])
def agregar():

    nombre = request.form["nombre"]
    precio = request.form["precio"]
    stock = request.form["stock"]

    conn = conectar()

    conn.execute(
        "INSERT INTO productos(nombre,precio,stock) VALUES(?,?,?)",
        (nombre, precio, stock)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/eliminar/<int:id>")
def eliminar(id):

    conn = conectar()

    conn.execute(
        "DELETE FROM productos WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    conn = conectar()

    if request.method == "POST":

        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        conn.execute(
            """
            UPDATE productos
            SET nombre=?, precio=?, stock=?
            WHERE id=?
            """,
            (nombre, precio, stock, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    producto = conn.execute(
        "SELECT * FROM productos WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "editar.html",
        producto=producto
    )

if __name__ == "__main__":
    app.run(debug=True)