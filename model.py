from flask_sqlalchemy import SQLAlchemy
from app import db

#todo: order_qty change to string, to prevent for integer overflow if user inserted a large integer
# or some other solution to be implemented
# add randomly generated ids for data

class Seller(db.Model):
    """
    Seller data
    """
    __tablename__ = "seller"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    phone_num = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    seller_img_name = db.Column(db.String())
    is_verified = db.Column(db.Integer)
    seller = db.relationship("Product", backref="seller")

    def __init__(self, full_name, city, state, address, phone_num, password, seller_img_name, is_verified):
        #self.id = id
        self.full_name = full_name
        self.city = city
        self.state = state
        self.address = address
        self.phone_num = phone_num
        self.password = password
        self.seller_img_name = seller_img_name
        self.is_verified = is_verified


class Buyer(db.Model):

    __tablename__ = "buyer"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    phone_num = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    buyer_img_name = db.Column(db.String())
    is_verified = db.Column(db.Integer)

    buyer = db.relationship("Order", backref="buyer")

    def __init__(self, full_name, city, state, address, phone_num, password, buyer_img_name, is_verified):
        #self.id = id
        self.full_name = full_name
        self.city = city
        self.state = state
        self.address = address
        self.phone_num = phone_num
        self.password = password
        self.buyer_img_name = buyer_img_name
        self.is_verified = is_verified


"""
class User(db.Model):

	store userdata

	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	full_name = db.Column(db.String(), nullable=False)
	city = db.Column(db.String(),nullable=False)
	state = db.Column(db.String(), nullable=False)
	address = db.Column(db.String(), nullable=False)
	phone_num = db.Column(db.Integer, nullable=False)
	password = db.Column(db.String(), nullable=False)
	#latitude = db.Column(db.float)
	#longitude = db.Column(db.float)
	#role = buyer or suplier
	order = db.relationship("Order", backref="user")

	def  __init__(self,full_name, city, state, address, phone_num, password):
		#self.id = id
		self.full_name = full_name
		self.city = city
		self.state = state
		self.address = address
		self.phone_num = phone_num
		self.password = password

"""


class Order(db.Model):
    """
    store orders of users ie cart
    """

    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    order_name = db.Column(db.String(), nullable=False)
    order_date = db.Column(db.String(), nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    order_price = db.Column(db.Integer)

    """
	Foreign keys
	"""
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"))
    buyer_id = db.Column(db.Integer, db.ForeignKey("buyer.id"))

    def __init__(self, order_name, order_date, order_qty, order_price, buyer_id, product_id):
        self.order_name = order_name
        self.order_date = order_date
        self.order_price = order_price
        self.order_qty = order_qty
        self.buyer_id = buyer_id
        self.product_id = product_id


class Product(db.Model):

    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(), nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)
    product_date = db.Column(db.String(), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    product_img_name = db.Column(db.String())

    order = db.relationship("Order", backref="order")
    """
	Foreign Key
	"""
    # relate to a category specified in category 
    category_id = db.Column(db.Integer, db.ForeignKey(
        "product_category.category_id"))

    # relate to seller, who added this product
    seller_id = db.Column(db.Integer, db.ForeignKey("seller.id"))

    def __init__(self, product_name, product_qty, product_date, product_price, product_img_name, seller_id, category_id):
        self.product_name = product_name
        self.product_qty = product_qty
        self.product_date = product_date
        self.product_price = product_price
        self.product_img_name = product_img_name
        self.category_id = category_id
        self.seller_id = seller_id


class Product_category(db.Model):
    """
    Store category image ie, grains, fruits
    """
    __tablename__ = "product_category"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(), nullable=False)
    category_image = db.Column(db.String(), nullable=False)

    # Relationship
    product_id = db.relationship("Product", backref="products")

    def __init__(self, category_name, category_image):
        self.category_name = category_name
        self.category_image = category_image


"""
class Product_img(db.Model):
	product_img_id = db.Column(db.Integer, primary_key=True)
	product_img_name = db.Column(db.Integer, primary_key=True)

	product = db.relationship("Product", backref="product")
"""
"""
class user_img(db.Model):
	user_img_id = db.Column(db.Integer, primary_key=True)

	seller_img = db.
"""


class Verify(db.Model):
    """
    store otp sent to user and verify it
    """
    __tablename__ = "verify"
    id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String(), nullable=False)
    otp = db.Column(db.Integer, nullable=False)

    def __init__(self, phone_num, otp):
        self.phone_num = phone_num
        self.otp = otp

# flask session table
class Sessions(db.Model):

    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255,convert_unicode=True), unique=True)
    data = db.Column(db.String())
    expiry = db.Column(db.String())

    def __init__(self,session_id,data,expiry):
        self.session_id = session_id
        self.data = data
        self.expiry = expiry