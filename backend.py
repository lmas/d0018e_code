import os, sys, secrets

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
            # Better or more obvious error handling?
            # sql_mode = "STRICT_ALL_TABLES",
            # get_warnings = True,
            # raise_on_warnings = True,
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


# Returns a list of products, with connector entries JOINed in.
# limit sets the maximum amount of products returned, if possible.
def get_products(db, limit=10):
    # TODO: gonna need args for group by/order by
    params = {"limit": limit}
    with db.cursor(dictionary=True) as cur:
        # The two joins basically adds extra values, from the connector table,
        # to the product tuples. No need to send extra SQL queries to check a
        # connector's type or gender!
        cur.execute(
            """
            SELECT
                p.*,
                c1.gender as "c1gender", c1.type as "c1type",
                c2.gender as "c2gender", c2.type as "c2type"
            FROM
                (SELECT * FROM Products LIMIT %(limit)s) p
                JOIN Connectors c1 ON p.idconnector1 = c1.idconnector
                JOIN Connectors c2 ON p.idconnector2 = c2.idconnector
            ;
            """,
            params,
        )
        rows = cur.fetchall()
    return rows


# Tries to insert a new user.
# Raises an IntegrityError if the email already exists (thanks to email UNIQUE constraint).
def register_user(db, email, pwd):
    # Use a dictionary, to be able to use it in the query
    params = {"email": email, "password": pwd}
    with db.cursor(dictionary=True) as cur:
        cur.execute("INSERT INTO Users(role, email, password) VALUES(0, %(email)s, %(password)s);", params)


# Simulates a login procedure (this is higly insecure! But it's not part of the course)
# It returns any user data, if the login was successfull.
def login_user(db, email, pwd):
    param = {"email": email, "password": pwd}
    with db.cursor(dictionary=True) as cur:
        cur.execute("""SELECT password, role FROM Users WHERE email=%(email)s LIMIT 1;""", param)
        row = cur.fetchone()
    if row is None:
        raise Exception("bad email")
    elif row["password"] != pwd:
        raise Exception("bad password")
    return row

def get_user(db, email):
    param = {"email": email}
    with db.cursor(dictionary=True) as cur:
        cur.execute("""SELECT password, first_name, last_name FROM Users WHERE email=%(email)s LIMIT 1;""", param)
        row = cur.fetchone()
    if row is None:
        raise Exception("bad email")
    return row

################################################################################
# FLASK APPLICATION AND PAGES


@app.route("/")
def page_home():
    db = get_db()
    rows = get_products(db, limit=5)
    db.close()
    return render_template("home.html", products=rows, genders=GENDERS)


@app.route("/about")
def page_about():
    return render_template("about.html")


@app.route("/product/<id>")
def page_product(id):
    return "product: " + id


@app.route("/register/")
def page_register():
    return render_template("register.html")


@app.route("/register/", methods=["POST"])
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


@app.route("/login/")
def page_login():
    return render_template("login.html")


@app.route("/login/", methods=["POST"])
def page_login_check():
    # Get email and password from request form
    email = get_str_form("email").lower()
    pwd = get_str_form("pwd")
    db = get_db()

    try:
        user = login_user(db, email, pwd)
        db.close()
    except mysql.connector.Error as err:
        db.close()
        print("Error while logging in: ", err)
        return "Bad login"
    except Exception as err:
        db.close()
        print("Bad login: ", err)
        return "Incorrect email/password"

    # All ok!
    session["email"] = email
    session["role"] = user["role"]
    flash("You were successfully logged in as " + email)
    return redirect(url_for("page_profile"))


@app.route("/logout/")
def page_logout():
    if session.get("email"):
        session.clear()
        flash("You were successfully logged out")
    return redirect(url_for("page_home"))

@app.route('/profile/')
def page_profile():
    db = get_db()
    error = 0
    # Convert to a dictionary, to be able to use it in the query
    param = {"email": session.get("email")}
    with db.cursor(dictionary=True) as cur:
        try:
            cur.execute("""SELECT iduser,first_name,last_name FROM Users WHERE email=%(email)s LIMIT 1;""", param)
            row = cur.fetchone()
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            error = 1
    db.close()
    if row is None:
        flash("Please log in before trying to view profile")
        return redirect(url_for('page_home'))
    if error == 1:
        flash("Something went wrong, please try again")
        return redirect(url_for('page_home'))
    return render_template("profile.html", userinfo=row)

@app.route('/changeprofile/')
def page_changeprofile():
    db = get_db()
    error = 0
    # Convert to a dictionary, to be able to use it in the query
    param = {"email": session.get("email")}
    with db.cursor(dictionary=True) as cur:
        try:
            cur.execute("""SELECT iduser,first_name,last_name FROM Users WHERE email=%(email)s LIMIT 1;""", param)
            row = cur.fetchone()
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            error = 1
    db.close()
    if row is None:
        flash("Please log in before trying to change your profile")
        return redirect(url_for('page_home'))
    if error == 1:
        flash("Something went wrong, please try again")
        return redirect(url_for('page_home'))
    return render_template("changeprofile.html")

@app.route('/changeprofile/', methods=['POST'])
def page_changeprofile_post():
    # Get all values from the form
    email = get_str_form("email").lower()
    pwd = get_str_form("pwd")
    fname = get_str_form('fName')
    lname = get_str_form('lName')
    error = 0
    # Connect to database, make sure no fields are empty and send the query
    db = get_db()
    row = get_user(db, session["email"])
    #db.close()
    if email == "":
       email = session["email"]
    if pwd == "":
        pwd = row["password"]
    if fname == "":
        fname = row["first_name"]
    if lname == "":
        lname = row["last_name"]
    param = {"oldEmail": session.get("email"), "email": email, "password": pwd, "first_name": fname, "last_name": lname}
    with db.cursor(dictionary=True) as cur:
        try:
            cur.execute(
                """
                UPDATE
                    Users
                SET
                    email=%(email)s,
                    password=%(password)s,
                    first_name=%(first_name)s,
                    last_name=%(last_name)s
                WHERE
                    email=%(oldEmail)s;
                """
                ,
                param
            )
            db.commit()
            db.close()
        except mysql.connector.Error as err:
            db.close()
            print("Error: {}".format(err))
            error = 1
    if error == 1:
        flash("Something went wrong, please try again")
        return redirect(url_for('page_home'))
    if session.get("email") != email:
        session["email"] = email
    return redirect(url_for('page_profile'))
    
################################################################################

if __name__ == "__main__":
    init_db()
    app.run()
