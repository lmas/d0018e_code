from flask import Flask
app = Flask(__name__)

# Get into correct terminal: source .venv/bin/activate
# Start with: python app.py

from flask import render_template

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
