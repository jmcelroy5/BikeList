import datetime
from app import db, model
from random import uniform, randrange, choice
import requests

def clear_bike_table():
	model.Bike.query.delete()
	db.session.commit()
	return "Bike table cleared!"

def clear_listings_table():
	model.Listing.query.delete()
	db.session.commit()
	return "Listings table cleared!"

def clear_users_table():
	model.User.query.delete()
	db.session.commit()
	return "Users table cleared!"

def get_all_bikes():
	bikes = model.Bike.query.all()
	for bike in bikes:
		print (bike.id, bike.title)

def populate_listings_SF():
	bike_list = model.Bike.query.all()
	for bike in bike_list[:40]:
		listing = model.Listing()

		listing.bike_id = bike.id
		listing.post_date = datetime.datetime.now()
		listing.post_expiration = datetime.datetime.now() + datetime.timedelta(30) # Post expires 30 days from now
		listing.post_status = "Active"
		listing.asking_price = randrange(100,1500)
		listing.latitude = 	uniform(37.75, 37.8) 			# Random lat in  SF 
		listing.longitude = uniform(-122.478,-122.4)  			# Random long in SF
		listing.additional_text = "This is a test bike. Isn't it beautiful?"
		db.session.add(listing)

	db.session.commit()
	rows = model.Listing.query.count()
	print rows, "listings generated successfuly!"

def populate_listings_EB():
	bike_list = model.Bike.query.all()
	for bike in bike_list[40:]:
		listing = model.Listing()

		listing.bike_id = bike.id
		listing.post_date = datetime.datetime.now()
		listing.post_expiration = datetime.datetime.now() + datetime.timedelta(30) # Post expires 30 days from now
		listing.post_status = "Active"
		listing.asking_price = randrange(100,1500)
		listing.latitude = 	uniform(37.79717, 37.89016)			# East Bay
		listing.longitude = uniform(-122.2968864, -122.243671)	# East Bay
		db.session.add(listing)

	db.session.commit()

	rows = model.Listing.query.count()
	print rows, "listings generated successfuly!"

def create_user():
	me = model.User()

	me.facebook_id = "2335427115026"
	me.first_name = "Jessica"
	me.last_name = "McElroy"
	me.email = "mcelroyjessica@gmail.com"
	me.avatar = "https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xpa1/v/t1.0-1/c32.0.50.50/p50x50/10169369_2128045370612_4824974463606072307_n.jpg?oh=84abbe14a17716d2e6b66d07a88f11f8&oe=54D23BF6&__gda__=1423797041_941578f05e56238a7887592bb802e207"
	me.facebook_url = "https://www.facebook.com/app_scoped_user_id/2335427115026/"

	db.session.add(me)
	db.session.commit()

	user = model.User.query.get(1)
	name = user.first_name
	print name, "added to database!"

# input a list of bike serial numbers
def populate_bikes(filename):

	f = open(filename, "r")

	serials = f.readlines()
	f.close()

	for serial in serials:
		# Create new bike instance for bike table
		new_bike = model.Bike()

		# Request bike from BikeIndex API
		bike_request = requests.get("https://bikeindex.org/api/v1/bikes?serial=" + str(serial))

		# Decode JSON 
		bike_json = bike_request.json()	 

		# Extract first bike from list
		if len(bike_json["bikes"]) == 0:
			print "No bike with serial number ", serial, " found"
			continue # go back to top of for-loop
		bike = bike_json["bikes"][0] 

		# Populate bike attributes
		new_bike.id = bike["id"]
		new_bike.user_id = 1 				# all bikes are belong to me 
		new_bike.size = bike["frame_size"]	
		new_bike.serial = bike["serial"]	
		new_bike.manufacturer = bike["manufacturer_name"]
		new_bike.rear_tire_narrow = bike["rear_tire_narrow"] 
		new_bike.type_of_cycle = bike["type_of_cycle"]
		new_bike.bikeindex_url = bike["url"]
		new_bike.photo = bike["photo"]
		new_bike.title = bike["manufacturer_name"] + " " + bike["frame_model"] 	# instead of API's bike title (bc they include colors)
		new_bike.thumb = bike["thumb"]
		new_bike.frame_model = bike["frame_model"]
		new_bike.year = bike["year"]
		new_bike.paint_description = bike["paint_description"] 
		new_bike.front_tire_narrow = bike["front_tire_narrow"]

		# Fudging frame material data to fill in gaps
		materials = ['Titanium','Carbon or composite','Aluminum']
		if new_bike.frame_material == None:
			new_bike.frame_material = choice(materials)

		# Fudging handlebar type to fill in gaps
		handlebars = ["Flat","Forward-facing","Rear-facing"]
		if new_bike.handlebar_type == None:
			new_bike.handlebar_type = choice(handlebars)

		# Fudging size data to fill in gaps
		print new_bike.size
		sizes = ['xs','s','m','l','xl']
		if new_bike.size is None or len(new_bike.size) == 0:
			new_bike.size = choice(sizes)
			print "is empty. Replaced with", new_bike.size

		if len(new_bike.size) > 0 and new_bike.size not in sizes:
			if new_bike.size.endswith('in'):
				# converting inches to centimeters
				size_convert = float(new_bike.size[:-2]) * 2.54
				print "inches converted to ", size_convert, "cm"
			elif new_bike.size.endswith('cm'):
				# floating the cm
				size_convert = float(new_bike.size[:-2])
				print "already in cm "
		else:
			size_convert = "no need to convert"
			new_bike.size_category = new_bike.size
			print size_convert
			print "put in size category: ", new_bike.size_category

		# put sizes into buckets 
		if type(size_convert) is float:
			if size_convert <= 50:
				new_bike.size_category = "xs"
				print "put in size category: ", new_bike.size_category
			elif size_convert > 50 and size_convert <= 53:
				new_bike.size_category = "s"
				print "put in size category: ", new_bike.size_category
			elif size_convert > 53 and size_convert <= 56:
				new_bike.size_category = "m"
				print "put in size category: ", new_bike.size_category
			elif size_convert > 56 and size_convert <= 59:
				new_bike.size_category = "l"
				print "put in size category: ", new_bike.size_category
			elif size_convert > 59:
				new_bike.size_category = "xl"
				print "put in size category: ", new_bike.size_category
			
		# breaking frame colors out of list format
		new_bike.frame_colors = "" 			
		for color in bike["frame_colors"]:
			new_bike.frame_colors += " " + color

		if bike["handlebar_type"] != None:
			new_bike.handlebar_type = bike["handlebar_type"].get("name", None)

		if bike["frame_material"] != None:
			new_bike.frame_material = bike["frame_material"].get("name", None)

		if bike["rear_wheel_size"] != None:
			new_bike.rear_wheel_size = bike["rear_wheel_size"].get("name", None)
			new_bike.rear_wheel_size_iso_bsd = bike["rear_wheel_size"].get("iso_bsd", None) 

		if bike["front_wheel_size"] != None:
			new_bike.front_wheel_size = bike["front_wheel_size"].get("name", None)	
			new_bike.front_wheel_size_iso_bsd = bike["front_wheel_size"].get("iso_bsd", None)	

		if bike["front_gear_type"] != None:
			new_bike.front_gear_type = bike["front_gear_type"].get("name", None)

		if bike["rear_gear_type"] != None:
			new_bike.rear_gear_type = bike["rear_gear_type"].get("name", None)

		# Add bike to session and commit changes
		db.session.add(new_bike)
	
	db.session.commit() 
	rows = model.Bike.query.count()
	return rows, "bikes added to database successfully"



