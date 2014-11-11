import datetime
import model
from random import uniform, randrange
import requests

def clear_bike_table():
	model.session.query(model.Bike).delete()
	model.session.commit()
	return "Bike table cleared!"

def clear_listings_table():
	model.session.query(model.Listing).delete()
	model.session.commit()
	return "Listings table cleared!"

def populate_listings():
	bike_list = model.session.query(model.Bike.id)
	for bike_id in bike_list:
		listing = model.Listing()

		listing.bike_id = bike_id[0]
		listing.post_date = datetime.datetime.now()
		listing.post_expiration = datetime.datetime.now() + datetime.timedelta(30) # Post expires 30 days from now
		listing.post_status = "Active"
		listing.asking_price = randrange(100,1500)
		listing.latitude = 	uniform(37.75, 37.8) 			# Random lat in SF
		listing.longitude = uniform(-122.478,-122.4)  		# Random long in SF
		listing.additional_text = "This is a test bike. Isn't it beautiful?"
		model.session.add(listing)

	model.session.commit()

	rows = model.session.query(model.Bike).count()

	print rows, "listings generated successfuly!"

# input a list of bike serial numbers
def populate_bikes(*serials):

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
		new_bike.serial = bike["serial"]	
		new_bike.manufacturer = bike["manufacturer_name"]
		new_bike.rear_tire_narrow = bike["rear_tire_narrow"] 
		new_bike.type_of_cycle = bike["type_of_cycle"]
		new_bike.bikeindex_url = bike["url"]
		new_bike.photo = bike["photo"]
		new_bike.thumb = bike["thumb"]
		new_bike.title = bike["title"]
		new_bike.frame_model = bike["frame_model"]
		new_bike.year = bike["year"]
		new_bike.paint_description = bike["paint_description"] 
		new_bike.front_tire_narrow = bike["front_tire_narrow"]

		new_bike.frame_colors = "" 			# breaking frame colors out of list format
		for color in bike["frame_colors"]:
			new_bike.frame_colors += color

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
		model.session.add(new_bike)
	
	model.session.commit() 

	rows = model.session.query(model.Bike).count()
	return rows, "bikes added to database successfully"

if __name__ == "__main__":
	# add_bikes(19012387006, "ABC123", "U79U19069", "U8YU51125", "U110U03441", "A1285895", "LX395331J", "M11060582", "C54D4515", "M130609389", "M12035406", "M11125025", "M11010768", "M13065C55", "U76P21332", "V1100S186")
	pass