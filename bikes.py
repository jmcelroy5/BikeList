from flask import Flask, render_template, request, redirect, url_for
from flask import session as flask_session
import datetime
import json
import model
import os,sys

app = Flask(__name__)

app.secret_key = 'abc123321cba'

@app.route("/")
def index():
	return render_template("getbike.html")

@app.route("/addbike", methods=['POST'])
def add_bike():
	""" Takes bike object from BikeIndex API and adds bike info to db"""

	bike_JSON= request.form.get("bike")	# Get JSON bike object from ajax ({bike: bikedata})
	bike = json.loads(bike_JSON)	# JSON string --> Python dictionary

	# Create new bike instance for bike table
	new_bike = model.Bike()

	# Populate bike attributes
	new_bike.id = bike["id"]	# primary key
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
	new_bike.paint_description = bike["paint_description"] # None
	new_bike.front_tire_narrow = bike["front_tire_narrow"]

	new_bike.frame_colors = "" 		# breaking frame colors out of list format
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
	# model.session.add(new_bike)
	# model.session.commit() 

	# Store bike id in flask session (to remember it for listing)
	flask_session["bike"] = bike["id"]

	return "Added bike to database"

@app.route("/listing")
def listing_form():
	return render_template("listing_form.html")

@app.route("/addlisting", methods=['POST'])
def add_listing():
	new_listing = model.Listing()

	new_listing.bike_id = flask_session["bike"]	# get bike id from flask session
	new_listing.post_date = datetime.datetime.now()
	new_listing.post_expiration = datetime.datetime.now() + datetime.timedelta(30) # Post expires 30 days from now
	new_listing.post_status = "active"
	new_listing.asking_price = request.form["price"] # FORM
	new_listing.latitude = request.form["latitude"] # FORM
	new_listing.longitude = request.form["longitude"] # FORM
	new_listing.additional_text = request.form["comments"] # FORM
	# also need to tie the listing to the logged-in user

	model.session.add(new_listing)
	model.session.commit()

	return "Listing added" # later this will flash message or something

@app.route("/listingsuccess") 
def listing_success():
	return render_template("listing_success.html")

if __name__== "__main__":
	app.run(debug = True)

