import os, sys

from flask import Flask, request, render_template
from flask import g as request_globals
import mysql.connector

# Loads ENVIRONMENT variables from a local file called ".env".
# This file SHOULD NOT be committed, as it contains secrets!
# Source: https://dev.to/sasicodes/flask-and-env-22am
from dotenv import load_dotenv

load_dotenv()

# Create the new flask app to be published
app = Flask(__name__)

################################################################################
# GLOBAL HELPER FUNCTIONS (these should be at the top of the file)


# Simple translation tables for showing prettier values as strings
ROLES = {0:"Customer", 1:"Administrator"}
GENDERS = {0:"male", 1:"female"}

# This function looks up the HTTP request's URL parameters and tries to return
# a string value stored under the parameter pointed to using "name".
# If the parameter wasn't found, a "default" value will be returned instead.
def get_str_param(name, default=""):
    value = default
    try:
        # Look the URL parameter in the current web request. For more info, see:
        # https://flask.palletsprojects.com/en/stable/api/#flask.Request.args
        value = str(request.args.get(name))
    except:
        pass
    # TODO: could do basic string validation to improve security?
    # But out of scope for this course..
    return value


# Similar function for looking up and returning an integer.
def get_int_param(name, default=0):
    value = default
    try:
        value = int(request.args.get(name))
    except:
        pass
    # TODO: integer validation?
    return value


################################################################################
# DATABASE FUNCTIONS

# get_db(), init_db(), and close_db() were sourced from:
# https://flask.palletsprojects.com/en/stable/tutorial/database/


# Helper for opening a new connection to the external db. Returns a db object.
def open_db():
    try:
        db = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_DATABASE"),

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
                for _ in cur.fetchsets(): pass

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


def get_products(db, limit=10):
    # TODO: gonna need args for group by/order by
    params = {"limit":limit}
    with db.cursor(dictionary=True) as cur:
        cur.execute("""
            SELECT
                p.*,
                c1.gender as "c1gender", c1.type as "c1type",
                c2.gender as "c2gender", c2.type as "c2type"
            FROM
                (SELECT * FROM Products LIMIT %(limit)s) p
                LEFT JOIN Connectors c1 ON p.connector1 = c1.id
                LEFT JOIN Connectors c2 ON p.connector2 = c2.id
            ;
            """, params)
        rows = cur.fetchall()
    return rows

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


################################################################################

if __name__ == "__main__":
    init_db()
    app.run()
