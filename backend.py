import os

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
    print("Connecting to database...")
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWD"),
        database=os.getenv("DB_DATABASE"),
    )


# Setups the db.
def init_db():
    print("Initialising database...")
    db = open_db()

    # Recreate the whole database
    with open("schemas/create_database.sql") as f:
        db.execute(f.read().decode("utf8"))


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


################################################################################
# FLASK APPLICATION AND PAGES

## --- BELOW TABLES COULD TO BE CONVERTED INTO CONSTANTS OR SOMETHING? ---
# -- Quick and dirty Color conversion table --
# Black     = 0
# White     = 1
# Red       = 2
# Yellow    = 3
# Green     = 4
# Blue      = 5
# Orange    = 6
# Brown     = 7
Colors = {
    "Black":    0,
    "White":    1,
    "Red":      2,
    "Yellow":   3,
    "Green":    4,
    "Blue":     5,
    "Orange":   6,
    "Brown":    7,
}

# -- Quick and dirty Connector table --
# Type A 1.0-1.1    = 0
# Type A SuperSpeed = 1
# Type B            = 2
# Type B SuperSpeed = 3
# Mini-A            = 4
# Mini-AB           = 5
# Mini-B            = 6
# Micro-A           = 7
# Micro-AB          = 8
# Micro-B           = 9
# Type-C            = 10

Connectors = {
	"Type A":				0,
	"Type A SuperSpeed":	1,
	"Type B":				2,
	"Type B SuperSpeed":	3,
	"Mini-A":				4,
	"Mini-AB":				5,
	"Mini-B":				6,
	"Micro-A":				7,
    "Micro-AB":				8,
    "Micro-B":				9,
    "Type-C":				10,
}

## --- END OF TABLES TO BE CONVERTED TO CONSTANTS ---

## --- FOR EASE OF USE WHILE ADDING A PRODUCT ---
# --- In what order Products table has the fields ---
# Products (Name, Price, Speed, Length, ImageFileName, Connector1, Connector2, Color)

# Values etc below taken from https://en.wikipedia.org/wiki/USB
# -- Quick and dirty Standards & Types table - Only allow these when adding them products (No mismatch of standards/types)? --
# USB 1.0			(Type-A 1.0, Type-B)
# USB 1.1           (Type-A 1.1, Type-B, Mini-A, Mini-AB, Mini-B)
# USB 2.0			(Typa-A 2.0, Type-B, Mini-A, Mini-AB, Mini-B)
# USB 2.0 Revised   (Typa-A 2.0, Type-B, Mini-A, Mini-AB, Mini-B, Micro-A, Micro-AB, Micro-B, Type-C)
# USB 3.0           (Type-A SuperSpeed, Type-B SuperSpeed, Micro-A SuperSpeed, Micro-AB SuperSpeed, Micro-B SuperSpeed, Type-C)
# USB 3.1           (Type-A SuperSpeed, Type-B SuperSpeed, Micro-A SuperSpeed, Micro-AB SuperSpeed, Micro-B SuperSpeed, Type-C)
# USB 3.2           (Type-A SuperSpeed, Type-B SuperSpeed, Micro-A SuperSpeed, Micro-AB SuperSpeed, Micro-B SuperSpeed, Type-C)
# USB4              (Type-C)
# USB4 2.0          (Type-C)

Standards_and_Types = {
	"USB 1.0":			["Type A", "Type B"],
	"USB 1.1":			["Type A", "Type B", "Micro A", "Micro AB", "Micro B"],
    "USB 2.0":			["Type A", "Type B", "Mini A", "Mini AB", "Mini B"],
    "USB 2.0 Revised":	["Type A", "Type B", "Mini A", "Mini AB", "Mini B", "Micro A", "Micro AB", "Micro B", "Type C"],
    "USB 3.0":			["Type A", "Type B", "Mini A", "Mini AB", "Mini B", "Micro A", "Micro AB", "Micro B", "Type C"],
    "USB 3.1":			["Type A", "Type B", "Mini A", "Mini AB", "Mini B", "Micro A", "Micro AB", "Micro B", "Type C"],
    "USB 3.2":			["Type A", "Type B", "Mini A", "Mini AB", "Mini B", "Micro A", "Micro AB", "Micro B", "Type C"],
    "USB4":				["Type C"],
    "USB4 2.0":			["Type C"],
}

# -- Quick and dirty Speed table --
# USB 1.0			1.5 Mbit/s, 12 Mbit/s
# USB 1.1           1.5 Mbit/s, 12 Mbit/s
# USB 2.0			480 Mbit/s
# USB 2.0 Revised   480 Mbit/s
# USB 3.0           5 Gbit/s (5000 Mbit/s)
# USB 3.1           10 Gbit/s (10000 Mbit/s)
# USB 3.2           20 Gbit/s (20000 Mbit/s)
# USB4              40 Gbit/s (40000 Mbit/s)
# USB4 2.0          80 Gbit/s (80000 Mbit/s)

Speeds = {
	"USB 1.0 Low-speed":	1.5,
	"USB 1.1 Low-speed":	1.5,
	"USB 1.0 High-speed":	12,
	"USB 1.1 High-speed":	12,
	"USB 2.0":				480,
	"USB 2.0 Revised":		480,
	"USB 3.0":				5000,
	"USB 3.1":				10000,
	"USB 3.1":				20000,
	"USB4":					40000,
	"USB4 2.0":				80000,
}

@app.route("/")
def page_home():
    return render_template("home.html")


@app.route("/about")
def page_about():
    return render_template("about.html")


################################################################################

if __name__ == "__main__":
    # TODO: run the db and test it!
    # init_db()
    app.run()
