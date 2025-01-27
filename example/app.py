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

c1 = prod("Coffee", "123", "https://upload.wikimedia.org/wikipedia/commons/4/45/A_small_cup_of_coffee.JPG")
c2 = prod("Coffee2", "987", "https://www.spectrumhealth.ie/wp-content/uploads/2017/11/steamingcupofcoffeewithspiltcoffeebeans-2048x1365.jpg.webp")
items = [c1, c2]

@app.route('/home/')
def hello():
    return render_template('home.html')

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