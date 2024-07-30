# Imports
from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from werkzeug.utils import secure_filename
import os, random, bcrypt, time

# Initialization
app = Flask(__name__)
conexion = sqlite3.connect(os.getcwd()+"\\database.sqlite", check_same_thread=False)
app.secret_key = "VHUgcHV0YSBtYWRyZSBjYWJyb25hem8gaGlqbyBkZSBwdXRhLCB5b3VyIGZ1Y2tpbmcgbW90aGVyIHNvbiBvZiBhIGJpdGNoLCBmdWNrIG9mZg"
db = conexion.cursor()
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin):
    def __init__(self, id, name, phone, address, password, prevAmount):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address
        self.password = password
        self.prevAmount = prevAmount

@login_manager.user_loader
def loader_user(user_id):
    data = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchall()
    user = []
    for item in data:
        user = item
    loggedUser = Users(id=user[0],
                        name=user[1],
                        phone=user[2],
                        password=user[3],
                        address=user[4],
                        prevAmount=int(user[5]))
    return loggedUser

# Rutas
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(id=random.randint(1000000000, 9999999999),
                    name=request.form.get("name"),
                    phone=request.form.get('phone'),
                    address=request.form.get("address"),
                    password=request.form.get("password").encode("utf-8"))
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(user.password, salt)
        db.execute("INSERT INTO users VALUES(?,?,?,?,?)", (user.id, user.name, user.phone, hashed, user.address))
        conexion.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone")
        password = request.form.get("password").encode("utf-8")
        data = db.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchall()
        user = []
        if len(data) > 0:
            for item in data:
                user = item
            loggedUser = Users(id=user[0],
                               name=user[1],
                               phone=user[2],
                               password=user[3],
                               address=user[4],
                               prevAmount=user[5])
            if bcrypt.checkpw(password, user[3]):
                login_user(loggedUser)
                return redirect("/")
            else:
                return render_template("login.html", alert="Contraseña incorrecta")
        else:
            return render_template("login.html", alert="Telefono no registrado")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

@app.route("/")
def home():
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("home.html", products=products)

@app.route("/addnew", methods=["GET", "POST"])
@login_required
def addnew():
    if request.method == 'POST':
        if 'img' not in request.files:
            print("not img")
            return redirect(request.url)
        file = request.files["img"]
        id=random.randint(1000000000, 9999999999)
        name = request.form.get("name")
        desc = request.form.get("desc")
        price = request.form.get("price")
        stock = request.form.get("stock")
        categ = request.form.get("categ")
        img = file.filename.replace(" ", "").replace("-", "_")
        db.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?, ?)", (id, name, desc, price, stock, categ, img))
        conexion.commit()
        if file:
            filename = secure_filename(img)
            file.save(os.path.join(os.getcwd()+'\\static\\imgs\\', filename))
        return redirect("/")
    return render_template("addnew.html")

@app.route("/cart/<phone>")
def cart(phone):
    if not current_user.is_authenticated:
        return redirect("/login")
    if phone != current_user.phone:
        return "404"
    products = db.execute("SELECT * FROM cart WHERE phone=?", (phone,)).fetchall()
    total = 0
    for item in products:
        total+=item[4]*item[6]
    if current_user.prevAmount == 0:
        discount = ((10*total)/100)
        return render_template("cart.html", products=products, total=(int(total)-discount), firstTime=True, discount=discount)
    elif current_user.prevAmount > 10000:
        discount = ((10*total)/100)
        return render_template("cart.html", products=products, total=(int(total)-discount), overSpent=True, discount=discount)
    return render_template("cart.html", products=products, total=total)

@app.route("/add_to_cart/<id>")
def addToCart(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    checkForExistingData = db.execute("SELECT * FROM cart WHERE phone=?", (current_user.phone,)).fetchall()
    for item in checkForExistingData:
        if item[7] == int(id):
            return redirect("/increment/"+str(item[0])+"/"+str(item[6]))
    product_data = db.execute("SELECT * FROM products WHERE id=?", (id,)).fetchall()
    data = {}
    for item in product_data:
        data = {
            "id": random.randint(1000000000, 9999999999),
            "phone": current_user.phone,
            "name": item[1],
            "desc": item[2],
            "price": item[3],
            "stock": item[4],
            "amount": 1,
            "product_id": item[0],
            "img": item[6]
        }
    db.execute("INSERT INTO cart VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (data["id"], 
                                                                      data["phone"], 
                                                                      data["name"], 
                                                                      data["desc"],
                                                                      data["price"], 
                                                                      data["stock"], 
                                                                      data["amount"], 
                                                                      data["product_id"], 
                                                                      data["img"]))
    conexion.commit()
    return redirect("/")

@app.route("/increment/<id>/<amount>")
def increment(id, amount):
    if not current_user.is_authenticated:
        return redirect("/login")
    product = db.execute("SELECT * FROM cart WHERE id=?", (id,))
    for item in product:
        if int(amount) == item[5]:
            return redirect("/cart/"+current_user.phone)
    db.execute("UPDATE cart SET amount=? WHERE id=?", (int(amount)+1, id))
    conexion.commit()
    return redirect('/cart/'+current_user.phone)
@app.route("/decrement/<id>/<amount>")
def decrement(id, amount):
    if not current_user.is_authenticated:
        return redirect("/login")
    if int(amount) == 1:
        db.execute("DELETE FROM cart WHERE id=?", (id,))
    else:
        db.execute("UPDATE cart SET amount=? WHERE id=?", (int(amount)-1, id))
    conexion.commit()
    return redirect('/cart/'+current_user.phone)

@app.route("/delete/<id>")
def deleteFromCart(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    db.execute("DELETE FROM cart WHERE id=?", (id,))
    conexion.commit()
    return redirect("/cart/"+current_user.phone)

@app.route("/categories/<categ>")
def categorias(categ):
    products = db.execute("SELECT * FROM products WHERE categ=?", (categ,)).fetchall()
    return render_template("home.html", products=products)


@app.route("/search", methods=["POST"])
def search():
    pattern = request.form.get("search")
    products = db.execute("SELECT * FROM products").fetchall()
    newProducts = []
    for item in products:
        if pattern in item[1]:
            newProducts.append(item)
        elif pattern in item[2]:
            newProducts.append(item)
    return render_template("home.html", products=newProducts)

@app.route("/pedir/<phone>/<total>")
def pedir(phone, total):
    if not current_user.is_authenticated:
        return redirect("/login")
    if not phone == current_user.phone:
        return redirect(f"/cart/{phone}")
    products = db.execute("SELECT * FROM cart WHERE phone=?", (current_user.phone,)).fetchall()
    if current_user.prevAmount == 0:
        total = int(round(float(total))) - ((10*int(round(float(total))))/100)
    data = {
            "id": random.randint(1000000000, 9999999999),
            "phone": current_user.phone,
            "name": current_user.name,
            "address": current_user.address,
            "time": time.strftime("%d/%m/%y - %I:%M"),
            "totalCost": total,
            "aceptado": 0,
            "ids": ",".join(str(item[7]) for item in products),
            "rechazado": 0,
            "amounts": ",".join(str(item[6]) for item in products)
        }
    db.execute("INSERT INTO pedidos VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data["id"],
                                                                data["name"],
                                                                data["phone"],
                                                                data["address"],
                                                                data["time"],
                                                                data["totalCost"],
                                                                data["aceptado"],
                                                                data["ids"],
                                                                data["rechazado"],
                                                                data["amounts"]))
    db.execute("DELETE FROM cart WHERE phone=?", (current_user.phone,))
    
    for item in products:
        stock = 0
        for i in db.execute("SELECT stock FROM products WHERE id=?", (item[7],)):
            stock = i[0]
        db.execute("UPDATE products SET stock=? WHERE id=?", (int(stock)-int(item[6]), item[7]))
    db.execute("UPDATE users SET amount=? WHERE phone=?", (current_user.prevAmount+int(total), current_user.phone))
    conexion.commit()
    return redirect("/")

@app.route("/pedidos")
def pedidos():
    if not current_user.is_authenticated:
        return redirect("/login")
    pedidos = db.execute("SELECT * FROM pedidos").fetchall()
    return render_template("pedidos.html", pedidos=pedidos)

@app.route("/pedidos/<phone>")
def pedidosCliente(phone):
    if not current_user.is_authenticated:
        return redirect("/login")
    pedidos = db.execute("SELECT * FROM pedidos WHERE phone=?", (phone,))
    return render_template("pedidosCliente.html", pedidos=pedidos)

@app.route("/delete-order/<id>")
def deleteOrder(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    db.execute("DELETE FROM pedidos WHERE id=?", (id,))
    conexion.commit()
    return redirect("/pedidos")

@app.route("/cancel/<id>")
def cancel(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    db.execute("DELETE FROM pedidos WHERE id=?", (id,))
    conexion.commit()
    return redirect(f"/pedidos/{current_user.phone}")

@app.route("/pedidos/productos/<id>")
def pedidosProductos(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    pedido = db.execute("SELECT * FROM pedidos WHERE id=?", (id,)).fetchall()
    ids = []
    amounts = []
    products = []
    currentLoopProduct = []
    counter = 0
    for item in pedido:
        ids = item[7].split(",")
        amounts = item[9].split(",")
    for item in ids:
        for product in db.execute("SELECT * FROM products WHERE id=?", (int(item),)).fetchall():
            for i in product:
                currentLoopProduct.append(i)
            currentLoopProduct.append(amounts[counter])
            products.append(currentLoopProduct)
            currentLoopProduct = []
            counter+=1
    return render_template("pedidosProductos.html", products=products, amounts=amounts)

@app.route("/aceptar/<id>")
def accept(id):
    db.execute("UPDATE pedidos SET aceptado=? WHERE id=?", (1, int(id)))
    conexion.commit()
    return redirect("/pedidos")

@app.route("/rechazar/<id>")
def reject(id):
    db.execute("UPDATE pedidos SET rechazado=? WHERE id=?", (1, int(id)))
    conexion.commit()
    return redirect("/pedidos")

if __name__ == "__main__":
    app.run(host="217.15.170.87", port=80, debug=True)