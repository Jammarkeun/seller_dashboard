from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    featured = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'quantity': self.quantity,
            'weight': self.weight,
            'image': self.image,
            'featured': self.featured,
            'date_added': self.date_added.isoformat()
        }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return redirect(url_for('homepage'))

@app.route('/homepage')
def homepage():
    products = Product.query.all()
    return render_template('homepage.html', products=products)

@app.route('/api/products')
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['productName']
        description = request.form['productDescription']
        price = float(request.form['productPrice'])
        category = request.form['productCategory']
        quantity = int(request.form['productQuantity'])
        weight = float(request.form['productWeight'])
        featured = 'featuredProduct' in request.form

        file = request.files['productImage']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename
        else:
            image = 'default.jpg'

        new_product = Product(name=name, description=description, price=price,
                              category=category, quantity=quantity, weight=weight,
                              image=image, featured=featured)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/dashboard')
def dashboard():
    products = Product.query.all()
    return render_template('seller_dashboard.html', products=products)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # This will drop all existing tables
        db.create_all()  # This will create new tables based on your current models
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)