import os, sys, secrets, time

from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask import g as request_globals
import mysql.connector

# Loads ENVIRONMENT variables from a local file called ".env".
# This file SHOULD NOT be committed, as it contains secrets!
# Source: https://dev.to/sasicodes/flask-and-env-22am
from dotenv import load_dotenv

load_dotenv()

# Create the new flask app to be published
app = Flask(__name__)

# This secret is used for the built-in flask sessions, how they work:
# https://flask.palletsprojects.com/en/stable/quickstart/#sessions
# Here we're randomizing the app.secret_key every time the server is restarted
app.secret_key = secrets.token_bytes()

################################################################################
# GLOBAL HELPER FUNCTIONS (these should be at the top of the file)


# Simple translation tables for showing prettier values as strings
ROLES = {0: "Customer", 1: "Administrator"}
GENDERS = {0: "male", 1: "female"}


# This function looks up the HTTP request's URL parameters and tries to return
# a string value stored under the parameter pointed to using "name".
# If the parameter wasn't found, a "default" value will be returned instead.
def get_str_param(name, default=""):
    try:
        # Lookup the URL parameter in the current web request. For more info, see:
        # https://flask.palletsprojects.com/en/stable/api/#flask.Request.args
        return request.args.get(name, default, str)
    except ValueError:
        # The type conversion failed, return default value
        return default
    # TODO: could do basic string validation to improve security?
    # But out of scope for this course..


# Similar function for looking up and returning an integer.
def get_int_param(name, default=0):
    try:
        return request.args.get(name, default, int)
    except ValueError:
        # The type conversion failed, return default value
        return default


# This function returns values from a submitted (POST) form, as strings.
def get_str_form(name, default=""):
    try:
        # https://flask.palletsprojects.com/en/stable/api/#flask.Request.form
        return request.form.get(name, default, str)
    except ValueError:
        return default


def get_int_form(name, default=""):
    try:
        return request.form.get(name, default, int)
    except ValueError:
        return default


def get_float_form(name, default=""):
    try:
        return request.form.get(name, default, float)
    except ValueError:
        return default


################################################################################
# DATABASE FUNCTIONS

# get_db(), init_db(), and close_db() were sourced from:
# https://flask.palletsprojects.com/en/stable/tutorial/database/


# Helper for opening a new connection to the external db. Returns a db object.
def open_db():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
        )
        return db
    except mysql.connector.Error as err:
        print("Error connecting to database:", err)
        print("\n--- Check host IP and if it's turned on! ---")
        sys.exit(1)


# Setup the db at app startup.
def init_db():
    db = open_db()
    with open("schemas/create_database.sql", encoding="utf-8") as f:
        try:

            with db.cursor() as cur:
                # Executes the whole SQL schema, where each SQL command run by itself
                # (thanks to the map_results=True)
                cur.execute(f.read(), map_results=True)

                # Then this next line must be executed to catch any syntax errors
                # in the SQL! Stupid mysql...
                for _ in cur.fetchsets():
                    pass

        except mysql.connector.Error as err:
            print("Error initialising database:", err)
            sys.exit(1)

    # Don't forget to commit the db changes and insertions!
    db.commit()
    db.close()


# Returns the current request's open db connection.
def get_db():
    # If it's not open yet, connect and save for later reuse.
    # The db is saved in the global variables for the request.
    if "db" not in request_globals:
        request_globals.db = open_db()
    return request_globals.db


# Close the db connection whenever the web request is being closed.
@app.teardown_request
def close_db(exception=None):
    # NOTE: ignore any passed exception for now. Exception handling in web requests
    # feels like it's out of the scope of the course.

    # Removes the db from the request's globals
    db = request_globals.pop("db", None)
    # And then closes the db if it was open (ie, not None)
    if db is not None:
        db.close()


# Tries to insert a new user.
# Raises an IntegrityError if the email already exists (thanks to email UNIQUE constraint).
def register_user(db, email, pwd):
    # Use a dictionary, to be able to use it in the query
    params = {"email": email, "password": pwd}
    with db.cursor(dictionary=True) as cur:
        cur.execute("INSERT INTO Users(role, email, password) VALUES(0, %(email)s, %(password)s);", params)


def get_user(db, email):
    param = {"email": email}
    with db.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM Users WHERE email=%(email)s LIMIT 1;", param)
        row = cur.fetchone()
    if row is None:
        raise Exception("bad user")
    return row


def update_user(db, param):
    with db.cursor(dictionary=True) as cur:
        cur.execute(
            """
            UPDATE Users
            SET email=%(email)s, password=%(password)s, first_name=%(first_name)s, last_name=%(last_name)s
            WHERE email=%(oldEmail)s;
        """,
            param,
        )


# Returns a list of products, with connector entries JOIN'ed in.
# limit sets the maximum amount of products returned, if possible.
def get_products(db, limit=10):
    # TODO: gonna need args for group by/order by
    params = {"limit": limit}
    with db.cursor(dictionary=True) as cur:
        # The two joins basically adds extra values, from the connector table,
        # to the product tuples. No need to send extra SQL queries to check a
        # connector's type or gender.
        # This was stolen from: https://dba.stackexchange.com/a/208083
        #
        # Any subqueries (queries inside a parenthesis) must also have an alias!
        # Source: https://stackoverflow.com/a/1888845
        cur.execute(
            """
            SELECT
                p.*,
                c1.gender as "c1gender", c1.type as "c1type",
                c2.gender as "c2gender", c2.type as "c2type"
            FROM
                (SELECT * FROM Products LIMIT %(limit)s) AS p
                JOIN Connectors c1 ON p.idconnector1 = c1.idconnector
                JOIN Connectors c2 ON p.idconnector2 = c2.idconnector;
        """,
            params,
        )
        rows = cur.fetchall()
    return rows


# get a single product
def get_product(db, id):
    param = {"idproduct": id}
    with db.cursor(dictionary=True) as cur:
        # Query stolen from above.
        cur.execute(
            """
            SELECT
                p.*,
                c1.gender as "c1gender", c1.type as "c1type",
                c2.gender as "c2gender", c2.type as "c2type"
            FROM
                (SELECT * FROM Products WHERE idproduct = %(idproduct)s LIMIT 1) p
                JOIN Connectors c1 ON p.idconnector1 = c1.idconnector
                JOIN Connectors c2 ON p.idconnector2 = c2.idconnector;
            """,
            param,
        )
        row = cur.fetchone()
    if id is None:
        raise Exception("bad id")

    return row


def get_connectors(db):
    with db.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM Connectors")
        rows = cur.fetchall()
    if rows is None:
        raise Exception("Connector table empty")
    return rows


def add_product(db, param):
    with db.cursor(dictionary=True) as cur:
        cur.execute(
            """
            INSERT INTO Products(price, in_stock, standard, length, color, idconnector1, idconnector2)
            VALUES( %(price)s, %(in_stock)s, %(standard)s, %(length)s, %(color)s, %(idcon1)s, %(idcon2)s );
        """,
            param,
        )


def remove_products(db, products):
    if len(products) < 1:
        raise Exception("No products selected")
    with db.cursor() as cur:
        # TODO: not sure if done efficiently using a transaction?
        # There's no need to start a transaction by hand, since the pkg does it
        # automagically for you (hence you need to call db.commit())
        # Source: https://stackoverflow.com/a/52723551
        cur.executemany("DELETE FROM Products WHERE idproduct = %s;", products)


################################################################################
# FLASK APPLICATION AND PAGES


@app.route("/")
def page_home():
    return render_template("home.html")


@app.route("/about")
def page_about():
    return render_template("about.html")


@app.route("/products")
def page_products():

    db = get_db()
    rows = get_products(db, limit=200)
    db.close()
    return render_template("products.html", products=rows, genders=GENDERS)


@app.route("/product/<id>")
def page_product(id):
    db = get_db()
    rows = get_product(db, id)
    db.close()
    return render_template("product.html", product=rows, genders=GENDERS)


@app.route("/register")
def page_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def page_register_post():
    # Get email and password from the submitted request form
    email = get_str_form("email").lower()
    pwd = get_str_form("pwd")
    db = get_db()

    try:
        register_user(db, email, pwd)
        db.commit()
        db.close()
    except mysql.connector.IntegrityError as err:
        # This error is thrown if the email already exists in the db
        db.close()
        print("Error inserting new user: ", err)
        return "Bad registration"
    except mysql.connector.Error as err:
        # More general, scarier error!
        db.close()
        print("Database failure during registration: ", err)
        return "Internal server error"

    # All ok, carry on!
    flash("Registration successful!")
    return redirect(url_for("page_home"))


@app.route("/login")
def page_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def page_login_post():
    # Get email and password from request form
    email = get_str_form("email").lower()
    pwd = get_str_form("pwd")
    db = get_db()

    try:
        user = get_user(db, email)
        db.close()
    except mysql.connector.Error as err:
        db.close()
        print("Error while logging in: ", err)
        return "Bad login"
    except Exception as err:
        db.close()
        print("Bad login: ", err)
        return "Incorrect email/password"
    if user["password"] != pwd:
        print("Bad login: ", err)
        return "Incorrect email/password"

    # All ok!
    session["email"] = email
    session["role"] = user["role"]
    session["id"] = user["iduser"]
    flash("You were successfully logged in as " + email)
    return redirect(url_for("page_profile"))


@app.route("/logout")
def page_logout():
    if session.get("email"):
        session.clear()
        flash("You were successfully logged out")
    return redirect(url_for("page_home"))


@app.route("/profile")
def page_profile():
    if session.get("email") is None:
        flash("Please log in before trying to view profile")
        return redirect(url_for("page_home"))

    db = get_db()
    try:
        user = get_user(db, session.get("email"))
        db.close()
    # Technically, no errors should be thrown here as the user is already logged in.
    except Exception as err:
        db.close()
        print("Error getting user profile: ", err)
        flash("Something went wrong, please try again")
        return redirect(url_for("page_home"))

    return render_template("profile.html", userinfo=user)


@app.route("/profile/update")
def page_profile_update():
    if session.get("email") is None:
        flash("Please log in before trying to change your profile")
        return redirect(url_for("page_home"))

    db = get_db()
    try:
        user = get_user(db, session.get("email"))
        db.close()
    # Technically, no errors should be thrown here as the user is already logged in.
    except Exception as err:
        db.close()
        print("Error getting user profile: ", err)
        flash("Something went wrong, please try again")
        return redirect(url_for("page_home"))

    return render_template("changeprofile.html", userinfo=user)


@app.route("/profile/update", methods=["POST"])
def page_profile_update_post():
    if session.get("email") is None:
        flash("Please log in before trying to change your profile")
        return redirect(url_for("page_home"))

    # Get all values from the form
    param = {
        "oldEmail": session.get("email"),
        "email": get_str_form("email").lower(),
        "password": get_str_form("pwd"),
        "first_name": get_str_form("fName"),
        "last_name": get_str_form("lName"),
    }
    # Connect to database, make sure no fields are empty and send the query
    db = get_db()
    try:
        update_user(db, param)
        # DONT FORGET TO COMMIT THE UPDATE/INSERT
        db.commit()
        db.close()
    except mysql.connector.Error as err:
        db.close()
        print("Error: {}".format(err))
        flash("Something went wrong, please try again")
        return redirect(url_for("page_home"))

    # Retain the new updated email in current session
    session["email"] = param["email"]
    return redirect(url_for("page_profile"))


@app.route("/products/new")
def page_products_new():
    # Only reachable if you're logged in, and has admin role
    if session.get("role") != 1:
        flash("Insufficient permissions")
        return redirect(url_for("page_home"))

    # Get all connectors and handle errors
    db = get_db()
    try:
        conn = get_connectors(db)
        db.close()
    except mysql.connector.Error as err:
        db.close()
        print("Error: {}".format(err))
        flash("Error while getting connectors")
        return redirect(url_for("page_products_new"))
    return render_template("addproduct.html", connectors=conn)


@app.route("/products/new", methods=["POST"])
def page_products_new_post():
    if session.get("role") != 1:
        flash("Insufficient permissions")
        return redirect(url_for("page_home"))

    # Place values in a dict so it can be used in the sql query
    param = {
        "price": get_int_form("price"),
        "in_stock": get_int_form("in_stock"),
        "standard": get_float_form("standard"),
        "length": get_float_form("length"),
        "color": get_str_form("color").lower(),
        "idcon1": get_int_form("idcon1"),
        "idcon2": get_int_form("idcon2"),
    }
    db = get_db()
    try:
        add_product(db, param)
        # DONT FORGET TO COMMIT THE UPDATE/INSERT
        db.commit()
        db.close()
    except mysql.connector.Error as err:
        db.close()
        print("Error: {}".format(err))
        flash("Error while inserting product in database")
        return redirect(url_for("page_products_new"))

    flash("Successfully added product")
    return redirect(url_for("page_products_new"))


@app.route("/products/remove")
def page_products_remove():
    if session.get("role") != 1:
        flash("Insufficient permissions")
        return redirect(url_for("page_home"))

    db = get_db()
    try:
        prods = get_products(db, limit=200)
        db.close()
    except mysql.connector.Error as err:
        db.close()
        print("Error while getting products: ", err)
        flash("Error while getting products")
        return redirect(url_for("page_products_remove"))
    return render_template("removeproducts.html", products=prods, genders=GENDERS)


@app.route("/products/remove", methods=["POST"])
def page_products_remove_post():
    if session.get("role") != 1:
        flash("Insufficient permissions")
        return redirect(url_for("page_home"))

    # Grabs the list of product IDs and convert each item to a tuple.
    # the cur.executemany() in remove_products() wants a list of tuples!
    # For an example of the list of tuples, see:
    # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-executemany.html
    products = [(id,) for id in request.form.getlist("products", type=int)]
    db = get_db()
    try:
        remove_products(db, products)
        db.commit()
        db.close()
    except Exception as err:
        db.close()
        print("Error while removing products: ", err)
        flash("Error while removing products")
        return redirect(url_for("page_products_remove"))

    flash("Successfully removed " + str(len(products)) + " products")
    return redirect(url_for("page_products_remove"))

# Help function to get all items in shoppingcart, total price and which items exceed stock amount
def get_shoppingcart(db):
    products = []
    stockProblem = []
    price = 0
    amountError = 0
    param = {"email": session.get("email"), "id": session.get("id")}
    with db.cursor(dictionary=True) as cur:
        try:
            cur.execute("""
                        SELECT idproduct, amount
                        FROM ShoppingCarts
                        WHERE iduser=%(id)s
                        ;""", param)
            rows = cur.fetchall()
            for row in rows:
                product = get_product(db, row["idproduct"])
                product["amount"] = row["amount"]
                price += row["amount"] * product["price"]
                products.append(product)
                if row["amount"] > product["in_stock"]:
                    product["amount"] = row["amount"]
                    stockProblem.append(product)
        except mysql.connector.Error as err:
            db.close()
            print("Error: {}".format(err))
            raise Exception("Error while getting shoppingcart")
    return products, price, stockProblem

# Help function to empty the shoppingcart, will happen once everything has been moved to the order table
def empty_shoppingcart(db):
    param = {"email": session.get("email"), "id": session.get("id")}
    with db.cursor(dictionary=True) as cur:
        try:
            cur.execute("""DELETE FROM ShoppingCarts WHERE iduser=%(id)s;""", param)
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            raise Exception("Error while emptying shoppingcart")
    return

# Help function to reduce in_stock, should happen once for every item
def reduce_stock(db, id, amount):
    with db.cursor(dictionary=True) as cur:
        try:
            prod = get_product(db, id)
            new_stock = prod["in_stock"] - amount
            if new_stock < 0:
                raise Exception("Too few items in stock.")
            param = {"idProduct": id, "new_stock": new_stock}
            cur.execute("""
                        UPDATE Products
                        SET in_stock=%(new_stock)s
                        WHERE idProduct=%(idProduct)s;
                        ;"""
                        , param)
        except Exception as err:
            flash("Error: {}".format(err))
            raise Exception("Error occured while reducing stock.")
    return

# Help function to place order (move from shoppingcart to orders)
def place_order(db):
    products = []
    # Using a standardized time to simplify grouping
    epoch_time = int(time.time())
    param = {"email": session.get("email"), "id": session.get("id")}
    with db.cursor(dictionary=True) as cur:
        try:
            products, price, stockProblem = get_shoppingcart(db)
            for prod in products:
                prod["timestamp"] = epoch_time
                prod["iduser"] = param["id"]
                cur.execute("""
                            INSERT INTO Orders(iduser, idproduct, amount, price, timestamp) 
                            VALUES (%(iduser)s, %(idproduct)s, %(amount)s, %(price)s, %(timestamp)s)
                            ;"""
                            , prod)
                reduce_stock(db, prod["idproduct"], prod["amount"])
            empty_shoppingcart(db)
            db.commit()
        except Exception as err:
            db.close()
            flash("Error: {}".format(err))
            raise Exception("Error occured while moving from shoppingcart to order.")
    return products, price, stockProblem

@app.route('/checkout')
def page_checkout():
    stockProblem = []
    # Make sure they're logged in before trying to reach checkout page
    if session.get("email") is None:
        flash("Please log in before trying to checkout")
        return redirect(url_for("page_home"))
    # Setup for queries etc
    products = []
    stockProblem = []
    price = 0
    db = get_db()
    try:
        products, price, stockProblem = get_shoppingcart(db)
        db.close()
    except:
        db.close()
        raise Exception("Error while getting shoppingcart")
    if len(stockProblem) != 0:
        flash("Note: Number of items exceed items in stock")
        return render_template("shoppingcart.html", products=products, genders=GENDERS, stockProblem=stockProblem)
    if len(products) == 0:
        flash("No items in shopping cart, please add some items before checking out")
        return redirect(url_for('page_products'))
    return render_template("checkout.html", products=products, genders=GENDERS, stockProblem=stockProblem, price=price)

@app.route('/checkout', methods=['POST'])
def page_checkout_order():
    # Make sure they're logged in before trying to reach checkout page
    if session.get("email") is None:
        flash("Please log in before trying to checkout")
        return redirect(url_for("page_home"))
    db = get_db()
    try:
        products, price, stockProblem = place_order(db)
        db.close()
    except:
        flash("Error occured while placing order, check amounts")
        return render_template('shoppingcart.html', products=products, genders=GENDERS, stockproblem=stockProblem)
    flash("Order registered, thank you for shopping with USB-R-US")
    return render_template('ordersuccessful.html', products=products, genders=GENDERS, price=price)
################################################################################

if __name__ == "__main__":
    # Delay the backend startup when it's being run inside docker,
    # as the mysql container starts up too slowly!
    delay = int(os.getenv("DB_DELAY", default=0))
    time.sleep(delay)

    # Start the app
    init_db()
    app.run(host="0.0.0.0")
