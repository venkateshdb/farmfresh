from app import db


class User(db.Model):
	"""
	store userdata
	@user_id
	@first name
	@last name
	@phone number
	
	"""
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	full_name = db.Column(db.String(), nullable=False)
	city = db.Column(db.String(),nullable=False)
	state = db.Column(db.String(), nullable=False)
	address = db.Column(db.String(), nullable=False)
	phone_num = db.Column(db.Integer, nullable=False)
	password = db.Column(db.String(), nullable=False)
	latitude = db.Column(db.float)
	longitude = db.Column(db.float)


class Order(db.Model):
	"""
	store orders of users
	"""

	__tablename__ = "orders"

	id = db.Column(db.Integer, primary_key=True)

