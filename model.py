from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, update, Boolean
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session 

ENGINE = create_engine("sqlite:///bikelist.db", echo=False) 
session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

Base = declarative_base()

## Class declarations

class Bike(Base):
	__tablename__ = "bikes"

	id = Column(Integer, primary_key = True)	# Bike Index id 
	
	# Required attributes to add a bike to BikeIndex (according to API docs)
	serial = Column(String(20), nullable=False)
	manufacturer = Column(String(64), nullable=True)
	frame_colors = Column(String(64), nullable=True)
	rear_tire_narrow = Column(Boolean, nullable=True)
	rear_wheel_size = Column(String(10), nullable=True) 
	rear_wheel_size_iso_bsd = Column(Integer, nullable=True)

	# Pretty certain these are inherently required
	type_of_cycle = Column(String(20), nullable=True) # subclasses for Bike?? 
	bikeindex_url = Column(String(64), nullable=True)
	# stolen = Column(Integer, nullable=False)		# Not including this - all bikes should be vetted

	# Attributes I might want to require for valid listing
	photo = Column(String(64), nullable=True)
	thumb = Column(String(64), nullable=True)
	handlebar_type = Column(String(20), nullable=True)	

	# Secondary attributes
	title = Column(String(50), nullable=True) 	# e.g."2014 Jamis Aurora (black)"
	frame_model = Column(String(50), nullable=True)
	year = Column(Integer, nullable=True)
	paint_description = Column(String(64), nullable=True)
	front_tire_narrow = Column(Boolean, nullable=True) 
	frame_material = Column(String(30), nullable=True) 	
	front_wheel_size = Column(String(10), nullable=True) 
	front_wheel_size_iso_bsd = Column(Integer, nullable=True)
	front_gear_type = Column(String(10), nullable=True)	
	rear_gear_type = Column(String(10), nullable=True)	

	# Bike also has listings attribute

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key = True)	
	# Get user info from FB: name, email, city, profile pic, etc

	# User also has listings

class Listing(Base):
	__tablename__ = "listings"

	id = Column(Integer, primary_key = True)	# Will this autogenerate?
	user_id = Column(Integer, ForeignKey('users.id'))
	bike_id = Column(Integer, ForeignKey('bikes.id'))

	user = relationship("User", backref=backref("listings"))
	bike = relationship("Bike", backref=backref("listings"))

	# post_date
	# last_modified
	# post_expiration
	# post_status 			# status code to allow for incomplete/inactive listings
	# asking_price
	# location
	# additional_text

def create_tables():
    engine = create_engine("sqlite:///bikelist.db", echo=True)
    Base.metadata.create_all(engine)

def main():
	""" in case I need it for something """

if __name__ == "__main__":
	main()






