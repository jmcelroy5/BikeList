# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine, ForeignKey, UniqueConstraint
# from sqlalchemy import db.Column, db.Integer, db.String, DateTime, update, Boolean, Float, func
# from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session 
from app import db
import datetime

# ENGINE = create_engine("sqlite:///bikelist.db", echo=False) 
# session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False))

# Base = declarative_base()
# Base.query = session.query_property()

# Base = declarative_base()

## Class declarations

class Bike(db.Model):
	__tablename__ = "bikes"

	id = db.Column(db.Integer, primary_key = True)	# Bike Index id 
	
	# Required attributes to add a bike to BikeIndex (according to API docs)
	serial = db.Column(db.String(20), nullable=False)
	manufacturer = db.Column(db.String(64), nullable=True)
	frame_colors = db.Column(db.String(64), nullable=True)
	rear_tire_narrow = db.Column(db.Boolean, nullable=True)
	rear_wheel_size = db.Column(db.String(10), nullable=True) 
	rear_wheel_size_iso_bsd = db.Column(db.Integer, nullable=True)

	# Pretty certain these are inherently required
	type_of_cycle = db.Column(db.String(20), nullable=True) # subclasses for Bike?? 
	bikeindex_url = db.Column(db.String(64), nullable=True)
	# stolen = db.Column(db.Integer, nullable=False)		# Not including this - all bikes should be vetted

	# Attributes I might want to require for valid listing
	size = db.Column(db.String(5), nullable=True)
	photo = db.Column(db.String(64), nullable=True)
	thumb = db.Column(db.String(64), nullable=True)
	handlebar_type = db.Column(db.String(20), nullable=True)	

	# Secondary attributes
	title = db.Column(db.String(50), nullable=True) 	# e.g."2014 Jamis Aurora (black)"
	frame_model = db.Column(db.String(50), nullable=True)
	year = db.Column(db.Integer, nullable=True)
	paint_description = db.Column(db.String(64), nullable=True)
	front_tire_narrow = db.Column(db.Boolean, nullable=True) 
	frame_material = db.Column(db.String(30), nullable=True) 	
	front_wheel_size = db.Column(db.String(10), nullable=True) 
	front_wheel_size_iso_bsd = db.Column(db.Integer, nullable=True)
	front_gear_type = db.Column(db.String(10), nullable=True)	
	rear_gear_type = db.Column(db.String(10), nullable=True)	

	# Bike also has listings attribute

class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key = True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(64)) # encrypt or something???
	avatar = db.Column(db.String(120))	# profile photo
	# Get user info from FB?

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):	# Try/except?
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)

	def __repr__(self):
		return '<User %r>' % self.first_name


	# User also has listings 

class Listing(db.Model):
	__tablename__ = "listings"

	id = db.Column(db.Integer, primary_key = True)	# Will this autogenerate?
	# user_id = db.Column(db.Integer, ForeignKey('users.id'))
	bike_id = db.Column(db.Integer, db.ForeignKey('bikes.id'), nullable=False) # unique = true ?

	# user = db.relationship("User", backref=backref("listings"))
	bike = db.relationship("Bike", backref=db.backref("listings"))

	post_date = db.Column(db.DateTime, nullable=False)
	post_expiration = db.Column(db.DateTime, nullable=True)
	post_status = db.Column(db.String(15), nullable=True)		# status code to allow for incomplete/inactive listings
	asking_price = db.Column(db.Integer, nullable=True)
	latitude = db.Column(db.Float, nullable=True)
	longitude = db.Column(db.Float, nullable=True)
	additional_text = db.Column(db.String(500),nullable=True)

def create_tables():
    # engine = create_engine("sqlite:///bikelist.db", echo=True)
    db.Model.metadata.create_all(db.engine)

def main():
	""" in case I need it for something """

if __name__ == "__main__":
	main()






