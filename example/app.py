from flask import Flask
import MySQLdb
from flask import render_template

db = None
cur = None

def dbConnect():
    global db, cur
    db = MySQLdb.connect(host="13.51.70.120",
                    port=7070,    # your host, usually localhost
                    user="flask",         # your username
                    passwd="super_secret_flask",  # your password
                    db="base")        # name of the data base

    # you must update the Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    # Create image table
    cur.execute("DROP TABLE IF EXISTS Images;")
    cur.execute("CREATE TABLE IF NOT EXISTS Images(idImage VARCHAR(45) PRIMARY KEY, name VARCHAR(45), url VARCHAR(45));")
    cur.execute('INSERT INTO Images(idImage, name, url) VALUES("USB-2.0", "usb-2.0", "/static/images/usb-2.0.png"),("USB-C", "usb-c", "/static/images/usb-c.jpg"),("USB-mini", "usb-mini", "/static/images/usb-mini.PNG"),("USB-MICRO", "usb-micro", "/static/images/usb-micro.PNG"),("USB-B", "usb-b", "/static/images/usb-b.PNG");')


def getImages():
    # Connect to database and create a pointer
    dbConnect()
    cur.execute("SELECT * FROM Images;")
    # Create a list containing the products in case a product was added while on another page
    products = []
    for row in cur.fetchall():
        products.append(prod(row[0],row[1],row[2]))
    # Disconnect from database
    dbDisconnect()
    return products

def dbDisconnect():
    global db, cur
    # Close connection to database and close cursor object so they cant be used to access database
    cur.close()
    db.close()
    # Set cur and db to None, to indicate they're supposed to be closed
    db = None
    cur = None

app = Flask(__name__)

# Get into correct terminal: source .venv/bin/activate
# Start with: python app.py

class prod:
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url

# ("USB-2.0", "usb-2.0", "/static/images/usb-2.0.png"),("USB-C", "usb-c", "/static/images/usb-c.jpg"),("USB-mini", "usb-mini", "/static/images/usb-mini.PNG"),("USB-MICRO", "usb-micro", "/static/images/usb-micro.PNG"),("USB-B", "usb-b", "/static/images/usb-b.PNG")
#c = prod("", "", "/static/images/")
#c1 = prod("usb-2.0", "USB-2.0", "/static/images/usb-2.0.png")
#c2 = prod("usb-c", "USB-C", "/static/images/usb-c.jpg")
#c3 = prod("usb-mini", "USB-mini", "/static/images/usb-mini.PNG")
#c4 = prod("usb-micro", "USB-MICRO", "/static/images/usb-micro.PNG")
#c5 = prod("usb-b", "USB-B", "/static/images/usb-b.PNG")
#items = [c1, c2, c3, c4, c5]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products/')
def products():
    # Query server for a list of all items
    items = getImages()
    return render_template('products.html', productList=items)

@app.route('/info/')
def info():
    return render_template('info.html')

@app.route('/product/<productID>')
def product(productID):
    # Query the server for the information of the item w/ said productID
    items = getImages()
    for curr in items:
        if curr.id == productID:
            return render_template('product.html', item=curr)
    c3 = prod("Error: 404", "N/A", "https://cdn.pixabay.com/photo/2015/03/25/13/04/page-not-found-688965_1280.png")
    return render_template('product.html', item=c3)

if __name__ == '__main__':
    app.run(debug=True)
