from app import db

## Class declarations

class Bike(db.Model):
	__tablename__ = "bikes"

	id = db.Column(db.Integer, primary_key = True)	# Bike Index id
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

	user = db.relationship("User", backref=db.backref("bikes"))
	
	# Required attributes to add a bike to BikeIndex (according to API docs)
	serial = db.Column(db.String(50), nullable=False)
	manufacturer = db.Column(db.String(64), nullable=True)
	frame_colors = db.Column(db.String(64), nullable=True)
	rear_tire_narrow = db.Column(db.Boolean, nullable=True)
	rear_wheel_size = db.Column(db.String(10), nullable=True) 
	rear_wheel_size_iso_bsd = db.Column(db.Integer, nullable=True)

	# Pretty certain these are inherently required
	type_of_cycle = db.Column(db.String(20), nullable=True) # subclasses for Bike? 
	bikeindex_url = db.Column(db.String(64), nullable=True)
	# stolen = db.Column(db.Integer, nullable=False)		# Not including this - all bikes should be vetted

	# Attributes I might want to require for valid listing
	size = db.Column(db.String(20), nullable=True)
	size_category = db.Column(db.String(5), nullable=True)
	photo = db.Column(db.String(200), nullable=True)
	thumb = db.Column(db.String(200), nullable=True)
	handlebar_type = db.Column(db.String(20), nullable=True)	

	# Secondary attributes
	title = db.Column(db.String(50), nullable=True) 	# e.g."2014 Jamis Aurora (black)"
	frame_model = db.Column(db.String(50), nullable=True)
	year = db.Column(db.Integer, nullable=True)
	paint_description = db.Column(db.String(64), nullable=True)
	front_tire_narrow = db.Column(db.Boolean, nullable=True) 
	frame_material = db.Column(db.String(30), nullable=True) 	
	front_wheel_size = db.Column(db.String(20), nullable=True) 
	front_wheel_size_iso_bsd = db.Column(db.Integer, nullable=True)
	front_gear_type = db.Column(db.String(10), nullable=True)	
	rear_gear_type = db.Column(db.String(10), nullable=True)	

	# Bike also has listings attribute

	def __repr__(self):
		return '<Bike %r>' % (self.title)

class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key = True)
	facebook_id = db.Column(db.String(30), unique=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	email = db.Column(db.String(120), unique=True)
	avatar = db.Column(db.String(300))	# profile photo
	facebook_url = db.Column(db.String(120))

	# Store access token for FB/BI?

	def get_id(self):	
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)

	def __repr__(self):
		return '<User %r>' % self.first_name

	# User also has listings 
	# User also has bikes

class Listing(db.Model):
	__tablename__ = "listings"

	id = db.Column(db.Integer, primary_key = True)	

	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	bike_id = db.Column(db.Integer, db.ForeignKey('bikes.id'), nullable=False) 

	user = db.relationship("User", backref=db.backref("listings"))
	bike = db.relationship("Bike", backref=db.backref("listings"))

	post_date = db.Column(db.DateTime, nullable=False)
	post_expiration = db.Column(db.DateTime, nullable=True)
	post_status = db.Column(db.String(15), nullable=True) # status code to allow for incomplete/inactive listings
	asking_price = db.Column(db.Integer, nullable=True)
	latitude = db.Column(db.Float, nullable=True)
	longitude = db.Column(db.Float, nullable=True)
	additional_text = db.Column(db.String(2000),nullable=True)
	email = db.Column(db.String(120), nullable=False)

	# Listing also has comments attribute (list of comments about that bike)

	def __repr__(self):
		return '<Listing %r>' % (self.additional_text)

class Comment(db.Model):
	__tablename__ = "comments"

	id = db.Column(db.Integer, primary_key = True)	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))

	comment_text = db.Column(db.String(500), nullable=False)

	listing = db.relationship("Listing", backref=db.backref("comments"))

class Favorite(db.Model):
	__tablename__ = "favorites"
	
	id = db.Column(db.Integer, primary_key = True)	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))

	user = db.relationship("User", backref=db.backref("favorites"))

def create_tables():
    db.Model.metadata.create_all(db.engine)


