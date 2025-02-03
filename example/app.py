from flask import Flask
import MySQLdb
from flask import render_template

db = MySQLdb.connect(host="13.51.70.120",
                     port=7070,    # your host, usually localhost
                     user="flask",         # your username
                     passwd="super_secret_flask",  # your password
                     db="base")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("DROP TABLE Kalles_table;")
cur.execute("CREATE TABLE IF NOT EXISTS Kalles_table(id INTEGER AUTO_INCREMENT, PRIMARY KEY(id), string VARCHAR(45));")
cur.execute("INSERT INTO Kalles_table(string) VALUES('exempel string'),('exempel string');")
cur.execute("SELECT * FROM Kalles_table;")

# print all the first cell of all the rows
for row in cur.fetchall():
    print (row)

db.close()
app = Flask(__name__)

# Get into correct terminal: source .venv/bin/activate
# Start with: python app.py



class prod:
    def __init__(self, name, id, url):
        self.name = name
        self.id = id
        self.url = url

#c = prod("", "", "/static/images/")
c1 = prod("USB-2.0", "usb-2.0", "/static/images/usb-2.0.png")
c2 = prod("USB-C", "usb-c", "/static/images/usb-c.jpg")
c3 = prod("USB-mini", "usb-mini", "/static/images/usb-mini.PNG")
c4 = prod("USB-MICRO", "usb-micro", "/static/images/usb-micro.PNG")
c5 = prod("USB-B", "usb-b", "/static/images/usb-b.PNG")
items = [c1, c2, c3, c4, c5]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products/')
def products():
    # Query server for a list of all items

    return render_template('products.html', productList=items)

@app.route('/info/')
def info():
    return render_template('info.html')

@app.route('/product/<productID>')
def product(productID):
    # Query the server for the information of the item w/ said productID
    for curr in items:
        if curr.id == productID:
            return render_template('product.html', item=curr)
    c3 = prod("Error: 404", "N/A", "https://cdn.pixabay.com/photo/2015/03/25/13/04/page-not-found-688965_1280.png")
    return render_template('product.html', item=c3)

if __name__ == '__main__':
    app.run(debug=True)
