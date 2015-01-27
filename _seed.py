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

def populate_listings():
	bike_list = model.Bike.query.all()
	for bike in bike_list:
		listing = model.Listing()

		listing.bike_id = bike.id
		listing.user_id = 1
		listing.post_date = datetime.datetime.now()
		listing.post_expiration = datetime.datetime.now() + datetime.timedelta(30) 
		listing.post_status = "Active"
		listing.asking_price = randrange(100,1500)

		listing.additional_text = "Asymmetrical aesthetic Thundercats bicycle rights mustache Kickstarter cred organic kogi, stumptown put a bird on it. Single-origin coffee letterpress put a bird on it ugh sustainable. Lo-fi Pinterest church-key tofu, sustainable roof party banjo kale chips American Apparel Williamsburg mumblecore. Etsy beard PBR gastropub cray flexitarian. Sustainable yr mlkshk pickled tilde semiotics, Wes Anderson High Life chia ugh put a bird on it literally Banksy slow-carb squid. Tofu street art craft beer, brunch post-ironic paleo roof party meditation Tumblr banjo. Direct trade messenger bag swag pickled deep v."
		listing.email = "asdvalenzuela@gmail.com"
		db.session.add(listing)

	db.session.commit()
	rows = model.Listing.query.count()
	print rows, "listings generated successfuly!"

def listing_locations():
	listings = model.Listing.query.all()
	for listing in listings[:45]:
		listing.latitude = 	uniform(37.75, 37.8) 		# SF
		listing.longitude = uniform(-122.478,-122.4)	# SF
	for listing in listings[45:]:
		listing.latitude = 	uniform(37.79717, 37.89016)			# East Bay
		listing.longitude = uniform(-122.2968864, -122.243671)	# East Bay

def create_test_user():
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

# input a list of bike serial numbers from file
def populate_bikes(filename):

	f = open(filename, "r")

	serials = f.readlines()
	f.close()

	for serial in serials:
		print "Adding", serial
		# Create new bike instance for bike table
		new_bike = model.Bike()

		# Request bike from BikeIndex API
		bike_request = requests.get("https://bikeindex.org/api/v1/bikes?serial=" + str(serial))

		# Decode JSON 
		bike_json = bike_request.json()	 

		# Extract first bike from API response
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
		sizes = ['xs','s','m','l','xl']
		if new_bike.size is None or len(new_bike.size) == 0:
			new_bike.size = choice(sizes)

		if len(new_bike.size) > 0 and new_bike.size not in sizes:
			if new_bike.size.endswith('in'):
				# converting inches to centimeters
				size_convert = float(new_bike.size[:-2]) * 2.54
			elif new_bike.size.endswith('cm'):
				# floating the cm
				size_convert = float(new_bike.size[:-2])
		else:
			size_convert = "no need to convert"
			new_bike.size_category = new_bike.size

		# put sizes into buckets for search
		if type(size_convert) is float:
			if size_convert <= 50:
				new_bike.size_category = "xs"
			elif size_convert > 50 and size_convert <= 53:
				new_bike.size_category = "s"
			elif size_convert > 53 and size_convert <= 56:
				new_bike.size_category = "m"
			elif size_convert > 56 and size_convert <= 59:
				new_bike.size_category = "l"
			elif size_convert > 59:
				new_bike.size_category = "xl"

		# writing out sizes for better display
		size_to_display = {"xs": "Extra Small", "s":"Small", "m":"Medium", "l":"Large", "xl": "Extra Large" }
		if new_bike.size in sizes:
			new_bike.size = size_to_display[new_bike.size]
			
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

if __name__ == "__main__":
	model.create_tables()
	create_test_user()
	populate_bikes("_testbikes.txt")
	populate_listings()
