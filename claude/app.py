import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_bcrypt import Bcrypt
import stripe
from functools import wraps
import os


project_dir = os.path.dirname(__file__) + os.sep
print(project_dir)

app = Flask(
    __name__,
    template_folder=os.path.join(project_dir, 'templates/'),
    static_folder=os.path.join(project_dir, 'static/'),
)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # 'sqlite:///db.sqlite'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
stripe.api_key = 'your-stripe-secret-key'

bcrypt = Bcrypt(app)


@app.before_request
def load_user():
  if current_user.is_authenticated:
    current_user.backend = db.session.query(User).get(current_user.id)


# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Integer, default=0)

    date_joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    last_purchase = db.Column(db.DateTime)

    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'


class CreditPurchase(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  credits_purchased = db.Column(db.Integer)
  purchase_amount = db.Column(db.Numeric(10, 2))


# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)

    featured_image = db.Column(db.String)
    primary_image = db.Column(db.String)
    secondary_image = db.Column(db.String)

    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'


# Cart model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Cart {self.id}>'


# Checkout model
class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_charge_id = db.Column(db.String(50))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String, default='Pending')
    total_price = db.Column(db.Integer)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user is None:
            flash(f'User {email} not registered. Please register.', 'warning')
            return redirect(url_for('signup'))

        # convert from utf-8 string to binary
        hashed_pw = user.password.encode('utf-8')

        if bcrypt.check_password_hash(hashed_pw, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # hash password
        pw_hash = bcrypt.generate_password_hash(request.form['password'])

        # encode to utf-8 string
        encoded_hash = pw_hash.decode('utf-8')

        email = request.form['email']

        new_user = User(email=email, password=encoded_hash)

        if email == 'gabe.spradlin@gmail.com':
            new_user.is_admin = True

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/cart')
@login_required
def cart():
    items = []
    total = 0
    for cart_item in current_user.cart:
        product = Product.query.get(cart_item.product_id)
        item_total = product.price * cart_item.quantity
        items.append(
            {'name': product.name, 'quantity': cart_item.quantity, 'price': product.price, 'total': item_total})
        total += item_total

    return render_template('cart.html', items=items, total=total)


@app.route('/add-to-cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    cart_item = Cart(user_id=current_user.id, product_id=product.id)
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Create Stripe charge
        charge = stripe.Charge.create(
            amount=request.form['stripeAmount'],
            currency='usd',
            source=request.form['stripeToken'],
            description='Charge for {user.email}'
        )

        # Create Checkout object
        checkout = Checkout(user_id=current_user.id, stripe_charge_id=charge['id'])
        db.session.add(checkout)

        current_user.last_purchase = datetime.datetime.utcnow()

        # Clear user's cart
        for cart_item in current_user.cart:
            db.session.delete(cart_item)

        db.session.commit()

        return render_template('checkout_complete.html', checkout=checkout)

    total = 0
    for cart_item in current_user.cart:
        product = Product.query.get(cart_item.product_id)
        total += product.price * cart_item.quantity

    return render_template('checkout.html', total=total)


def admin_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if not current_user.is_admin:
      return abort(403)
    return f(*args, **kwargs)
  return decorated_function


def admin_users_data():
    # calculate dates
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(weeks=1)
    three_months_ago = now - datetime.timedelta(days=90)

    # get new users per week
    new_users = db.session.query(
        db.func.strftime('%W', User.date_joined).label('week'),
        db.func.count(User.id).label('new_users')
    ).group_by('week').all()

    # Extract weeks and counts
    weeks = [item[0] for item in new_users]
    counts = [item[1] for item in new_users]

    # Format dates
    week_starts = []
    for week in weeks:
        start_date = datetime.datetime.strptime(str(week) + '-0', "%W-%w")
        week_start = start_date.strftime("%m/%d/%Y")
        week_starts.append(week_start)

    # get active users
    active_users = User.query.filter(User.last_purchase != None, User.last_purchase > three_months_ago).count()

    # get total users
    total_users = User.query.count()

    return {
        'new_users':new_users,
        'week_starts': week_starts,
        'counts': counts,
        'active_users': active_users,
        'total_users': total_users
    }


@app.route('/admin')
@admin_required
def admin_index():
    data = admin_users_data()

    return render_template('admin/index.html',
                           new_users=data['new_users'],
                           week_starts=data['week_starts'],
                           counts=data['counts'],
                           active_users=data['active_users'],
                           total_users=data['total_users'])


@app.route('/admin/users')
@admin_required
def admin_users():
    data = admin_users_data()

    return render_template('admin/users.html',
                           new_users=data['new_users'],
                           week_starts=data['week_starts'],
                           counts=data['counts'],
                           active_users=data['active_users'],
                           total_users=data['total_users'])


@app.route('/admin/products')
@admin_required
def admin_products():
    # calculate dates
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(weeks=1)

    # get products with sales data
    products = db.session.query(
        Product.name,
        Product.description,
        db.func.sum(OrderItem.quantity).label('total_sold'),
        db.func.sum(OrderItem.quantity.filter(OrderItem.order_date > one_week_ago)).label('units_sold_1wk')
    ).join(OrderItem).group_by(Product.id).all()

    return render_template('admin/products.html', products=products)


@app.route('/admin/orders')
@admin_required
def admin_orders():
    # calculate dates
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(weeks=1)
    one_month_ago = now - datetime.timedelta(days=30)

    # revenue query
    revenue = db.session.query(
        db.func.sum(OrderItem.quantity * Product.price).label('revenue')
    ).join(Product).filter(Order.purchase_date > one_month_ago).scalar()

    # orders by day
    orders = Order.query.filter(Order.purchase_date > one_month_ago).group_by(
        db.func.strftime('%Y-%m-%d', Order.purchase_date)).count()

    # product orders query
    product_orders = db.session.query(
        Product.name,
        db.func.sum(OrderItem.quantity).label('total'),
        db.func.sum(OrderItem.quantity.filter(OrderItem.order_date > one_month_ago)).label('month'),
        db.func.sum(OrderItem.quantity.filter(OrderItem.order_date > one_week_ago)).label('week')
    ).join(OrderItem).group_by(Product.id).all()

    return render_template('admin/orders.html',
                           revenue=revenue,
                           orders=orders,
                           product_orders=product_orders)


if __name__ == '__main__':
    app.run(debug=True)
