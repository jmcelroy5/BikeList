from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, update
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
	# user_id = Column(Integer, ForeignKey('users.id'))
	# listing_id = Column(Integer, ForeignKey('bikes.id'))
	
	serial = Column(String(20), nullable = False)
	bikeindex_url = Column(String(64), nullable=False)
	photo = Column(String(64), nullable=True)

	manufacturer = Column(String(64), nullable=True)
	frame_model = Column(String(64), nullable=True)
	year = Column(Integer, nullable=True)
	
	frame_colors = Column(String(64), nullable=True)
	paint_description = Column(String(64), nullable=True)
	
	rear_tire_narrow = Column(String(10), nullable=True) # How to make this a boolean?
	front_tire_narrow = Column(String(10), nullable=True) # How to make this a boolean?
	
	title = Column(String(64), nullable=True) # Looks like "2014 Jamis Aurora (black)"
	
	rear_wheel_size = Column(String(10), nullable=True) #object
	front_wheel_size = Column(String(10), nullable=True) #object
	handlebar_type = Column(String(20), nullable=True)	#object
	frame_material = Column(String(20), nullable=True) 	#object
	front_gear_type = Column(String(5), nullable=True)	#object
	rear_gear_type = Column(String(5), nullable=True)	#object

	type_of_cycle = Column(String(20), nullable=False) # subclasses for Bike??
	stolen = Column(String(10), nullable=False)	# What would happen if bike WERE stolen?!

	user = relationship("User", backref=backref("bikes", order_by=id))

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key = True)	# Will this autogenerate?
	# Get from FB: name, email, city, profile pic, etc

	# Also has listings attribute (backref)
	# Also has bikes attribute (backref)

class Listing(Base):
	__tablename__ = "listings"

	id = Column(Integer, primary_key = True)	# Will this autogenerate?
	user_id = Column(Integer, ForeignKey('users.id'))
	bike_id = Column(Integer, ForeignKey('bikes.id'))

	user = relationship("User", backref=backref("listings", order_by=id))

	# post_date
	# last_modified
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






