import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "inventario-secreto"


def conectar():
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row
    return conn


def crear_tablas():
    conn = conectar()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        rut TEXT UNIQUE NOT NULL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL,
        lista TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()


crear_tablas()


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        nombre = request.form["nombre"]
        rut = request.form["rut"]

        conn = conectar()

        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE rut=?",
            (rut,)
        ).fetchone()

        if not usuario:

            conn.execute(
                "INSERT INTO usuarios(nombre,rut) VALUES(?,?)",
                (nombre, rut)
            )

            conn.commit()

            usuario = conn.execute(
                "SELECT * FROM usuarios WHERE rut=?",
                (rut,)
            ).fetchone()

        session["usuario_id"] = usuario["id"]
        session["nombre"] = usuario["nombre"]

        conn.close()

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/")
def inicio():

    if "usuario_id" not in session:
        return redirect("/login")

    conn = conectar()

    productos = conn.execute(
        """
        SELECT *
        FROM productos
        WHERE usuario_id=?
        ORDER BY id DESC
        """,
        (session["usuario_id"],)
    ).fetchall()

    total = sum(
        p["precio"] * p["stock"]
        for p in productos
    )

    conn.close()

    return render_template(
        "index.html",
        productos=productos,
        usuario=session["nombre"],
        total=total
    )


@app.route("/agregar", methods=["POST"])
def agregar():

    if "usuario_id" not in session:
        return redirect("/login")

    nombre = request.form["nombre"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    lista = request.form["lista"]

    conn = conectar()

    conn.execute(
        """
        INSERT INTO productos
        (nombre, precio, stock, lista, usuario_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            nombre,
            precio,
            stock,
            lista,
            session["usuario_id"]
        )
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/eliminar/<int:id>")
def eliminar(id):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = conectar()

    conn.execute(
        """
        DELETE FROM productos
        WHERE id=? AND usuario_id=?
        """,
        (id, session["usuario_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = conectar()

    if request.method == "POST":

        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        conn.execute(
            """
            UPDATE productos
            SET nombre=?, precio=?, stock=?
            WHERE id=? AND usuario_id=?
            """,
            (
                nombre,
                precio,
                stock,
                id,
                session["usuario_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    producto = conn.execute(
        """
        SELECT *
        FROM productos
        WHERE id=? AND usuario_id=?
        """,
        (id, session["usuario_id"])
    ).fetchone()

    conn.close()

    if not producto:
        return redirect("/")

    return render_template(
        "editar.html",
        producto=producto
    )


if __name__ == "__main__":
    app.run(debug=True)