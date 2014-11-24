from flask import render_template, request, jsonify, g, redirect, flash, url_for
from flask import session as flask_session
from model import Bike, Listing, User
import model
from app import app, db, facebook, bikeindex
import datetime
import json
import requests
import os
from math import ceil

@facebook.tokengetter
def get_facebook_token():
    return flask_session.get('facebook_token')

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None or 'access_token' not in resp:
    	flash("Facebook authentication error.")
        return redirect('/login')
    else:
    	flask_session['logged_in'] = True
    	flask_session['facebook_token'] = (resp['access_token'], '')

    	user = add_new_user()

    	flask_session['user'] = user.id # Store just the user id?

    	flash("You are logged in.")
    	return redirect(url_for('index')) # How to detect which page they were headed for?

    # call get_user to get id/email/whatever from fb
    # check if user already exists on our end (query db)
    # if not, call function to add new User


def add_new_user():
	""" Uses FB id to check for exisiting user in db. If none, adds new user."""
	fb_user = facebook.get('/me').data
	existing_user = db.session.query(User).filter(User.facebook_id == fb_user['id']).first()
	if existing_user is None:
		new_user = model.User()
		new_user.facebook_id = fb_user['id']
		new_user.first_name = fb_user['first_name']
		new_user.last_name = fb_user['last_name']
		new_user.email = fb_user['email']
		new_user.facebook_url = fb_user['link']
		new_user.avatar = get_user_photo()
		# commit new user to database
		db.session.add(new_user)
		db.session.commit()
		# Go get that new user
		new_user = db.session.query(User).filter(User.facebook_id == fb_user['id']).first()
		return new_user
	else:
		return existing_user

# login view
@app.route("/login")
def login():
	return render_template("login.html")

# def pop_login_session():
#     flask_session.pop('logged_in', None)
#     flask_session.pop('facebook_token', None)
#     flask_session.pop('user', None)

@app.route("/logout")
def logout():
    # pop_login_session()
    clear_session()
    flash("You are logged out.")

    return redirect('/')

@app.route('/clearsession')
def clear_session():
	flask_session['logged_in'] = None
	flask_session['facebook_token'] = None
	flask_session['BI_authorized'] = None
	flask_session['bikeindex_token'] = None
	flask_session['user'] = None
	return "Session cleared!"

@app.route('/getsession')
def get_session():
	print "\nLogged in:", flask_session.get('logged_in', 'Not set')
	print "\n Facebook token:", flask_session.get('facebook_token','Not set')
	print "\n BikeIndex authorized:", flask_session.get('BI_authorized', 'Not set')
	print "\n BikeIndex token:", flask_session.get('bikeindex_token', 'Not set')
	print "\n Current user:", flask_session.get("user", "Not set")
	return "Check the console."

@app.route("/_get_current_user")
def get_current_user():
	""" Get current user from session """
	return g.user

@app.route("/_get_user_photo")
def get_user_photo():
	photo = facebook.get('/me/picture?redirect=0&height=1000&type=normal&width=1000').data
	photo_url = photo['data']['url']
	print "\n\n\nTHIS IS THE PHOTO URL", photo_url
	return photo_url

# Bike Index OAuth Stuff:

@bikeindex.tokengetter # ???
def get_bikeindex_token():
	access_token = os.environ.get('BIKEINDEX_ACCESS_TOKEN')
	return access_token
    # return flask_session.get('bikeindex_token')

@app.route("/bikeindex_login") # ???
def bikeindex_login():
    return bikeindex.authorize(callback=url_for('bikeindex_authorized', _external=True))

@app.route("/bikeindex_authorized", methods=['GET','POST']) # ???
@bikeindex.authorized_handler
def bikeindex_authorized(resp):
	""" Running into error here (Flask Oauth exception: Invalid response from BikeIndex)"""
	flask_session['BI_authorized'] = True
	flask_session['bikeindex_token'] = resp['authenticity_token']
	print resp


@app.route("/getuser_bikeindex") # This works 
def user_data():
    """Grab user profile information from Bike Index."""
    access_token = os.environ.get('BIKEINDEX_ACCESS_TOKEN')
    BI_request = requests.get('https://bikeindex.org/api/v2/users/current?access_token=' + access_token)
    BI_user = BI_request.json()	 
    bikeindex_userdata = {
         	'bikeindex_user_id': BI_user['id'],
            'bike_ids': BI_user['bike_ids']
         }
    # Will put something here that stores user's bike ids in database
    return jsonify(bikeindex_userdata)

def add_user_bikes(user):
	# get user id from session
	pass

# Runs on browser refresh. Checks for current user and bike
@app.before_request
def get_current_user():
    user_id = flask_session.get('user', None)
    if user_id:
    	user = db.session.query(User).filter_by(id=user_id).one()
    	g.user = user.id
    	g.avatar = user.avatar
    	g.name = user.first_name
    	g.logged_in = True

# Make current user available on templates
@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}

@app.route("/")
def index():
	# Now home route just renders template and all content is generated by javascript
	return render_template("index.html")

@app.route("/getbikes")
def get_bikes():
	""" get search results """
	sizes = request.args.getlist('sizes[]') 		# returns list of names of checkboxes that are checked when form submits
	print "SIZES=========", sizes
	materials = request.args.getlist('materials[]') 		# returns list of names of checkboxes that are checked when form submits
	print "MATERIALS=========", materials
	# materials looks like: [u'Carbon or composite', u'Aluminum']
	handlebars = request.args.getlist('handlebars[]') 		# returns list of names of checkboxes that are checked when form submits
	print "HANDLEBARS=========", handlebars
	min_price = request.args.get('minPrice')
	print "MIN_PRICE=========", min_price
	max_price = request.args.get('maxPrice')
	print "MAX_PRICE=========", max_price

	print "search params object:", request.args
	lat_min = request.args.get('latitudeMin')
	lat_max = request.args.get('latitudeMax')
	long_min = request.args.get('longitudeMin')
	long_max = request.args.get('longitudeMax')
	print ("\n\n\n\n lat and long from search params", lat_min, lat_max, long_min, long_max)
	# Base query for active listings
	query = db.session.query(Listing, Bike).filter(Listing.bike_id == Bike.id, Listing.post_status=="Active") # Base query
	# query = Listing.query.join(Bike).filter(Listing.bike_id == Bike.id, Listing.post_status=="Active")

	# Filter for listings in current map view
	try:
		query = query.filter(Listing.latitude > float(lat_min)).filter(Listing.latitude < float(lat_max))
		query = query.filter(Listing.longitude > float(long_min)).filter(Listing.longitude < float(long_max))
		print ("\n\n\n\n", lat_min, lat_max, long_min, long_max)
	except ValueError:
		print "map has not been moved yet"
	except TypeError:
		print "map has not been moved yet"

	# Filters
	if sizes:
		query = query.filter(Bike.size_category.in_(sizes))
	if materials:	
		query = query.filter(Bike.frame_material.in_(materials))
	if handlebars:
		query = query.filter(Bike.handlebar_type.in_(handlebars))
	if min_price:
		query = query.filter(Listing.asking_price >= min_price)
	if max_price:
		query = query.filter(Listing.asking_price <= max_price)

	# Need to add size filter...
	# if size:
	# 	query = query.filter_by(things = foo)

	# get total number of listings found for this search before applying page limit
	total_count = query.count()

	# Default order by ascending price 
	all_listings = query.order_by(Listing.asking_price.asc())

	# find out what page is being requested
	current_page = int(request.args.get("currentPage"))
	# number of results per page
	limit = int(request.args.get("resultLimit"))

	print "\n \n \n CURRENT PAGE is ", current_page
	offset = current_page * limit
	print "\n \n \nOFFSET for this page is ", offset, type(offset)

	query = query.offset(offset)

	all_listings = query.limit(limit)	# Finish the query

	# Initializing response object
	response = {
		"listings": [],
		"num_results": all_listings.count(),
		"page_range_lower": None,
		"page_range_upper": None,
		"total_results": total_count
	}

	# Building final response object
	for listing, bike in all_listings:
		print bike
		response["listings"].append({
						'url': "/listing/" + str(bike.id),
						'latitude': listing.latitude, 
						'longitude': listing.longitude,
						'id': listing.id,
						'photo': bike.photo,
						'price': listing.asking_price,
						'material': bike.frame_material,
						'title': bike.title + " ($" + str(listing.asking_price) + ")"})
		if current_page == 0:
			response["page_range_lower"] = 1
		else:
			response["page_range_lower"] = offset + 1
		response["page_range_upper"] = response["page_range_lower"] + response["num_results"] - 1

	return jsonify(response=response)
		
@app.route("/sell")
def get_bike():
	if flask_session.get("logged_in", None) == True:
		return render_template("getbike.html")
	else:
		flash("Sign up to sell a bike on BikeList!")
		return redirect("/login")

@app.route("/fetchbike")
def fetch_bike():
	serial = request.args.get("serial")
	print "serial from form ", serial
	r = requests.get("https://bikeindex.org/api/v1/bikes?serial=" + serial)
	bike = r.json()
	print bike
	return jsonify(response=bike)

@app.route("/addbike", methods=['POST'])
def add_bike():
	""" Takes bike object from BikeIndex API and adds bike info to db"""

	bike_JSON= request.form.get("bike")	# Get JSON bike object from ajax ({bike: bikedata})
	bike = json.loads(bike_JSON)	# JSON string --> Python dictionary

	# Create new bike instance for bike table
	new_bike = Bike()

	# Populate bike attributes
	new_bike.id = bike["id"]	# primary key
	new_bike.serial = bike["serial"]	
	new_bike.size = bike["frame_size"]
	new_bike.manufacturer = bike["manufacturer_name"]
	new_bike.rear_tire_narrow = bike["rear_tire_narrow"] 
	new_bike.type_of_cycle = bike["type_of_cycle"]
	new_bike.bikeindex_url = bike["url"]
	new_bike.photo = bike["photo"]
	new_bike.thumb = bike["thumb"]
	new_bike.title = bike["manufacturer_name"] + " " + bike["frame_model"]
	new_bike.frame_model = bike["frame_model"]
	new_bike.year = bike["year"]
	new_bike.paint_description = bike["paint_description"] # None
	new_bike.front_tire_narrow = bike["front_tire_narrow"]

	# list of valid size categories 
	valid_sizes = ['xs','s','m','l','xl']

	# normalizing frame size measurements (inches to cm)
	if len(new_bike.size) > 0 and new_bike.size not in valid_sizes:
		if new_bike.size.endswith('in'):
			# converting inches to centimeters
			size_convert = float(new_bike.size[:-2]) * 2.54
		elif new_bike.size.endswith('cm'):
			# floating the cm
			size_convert = float(new_bike.size[:-2])
	else:
		size_convert = "no need to convert"
		new_bike.size_category = new_bike.size

	# putting sizes into categories
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

@app.route("/list")
def listing_form():
	return render_template("listing_form.html")

@app.route("/addlisting", methods=['POST'])
def add_listing():

	new_listing = Listing()

	new_listing.bike_id = flask_session["bike"]	# get bike id from flask session
	new_listing.post_date = datetime.datetime.now()
	new_listing.post_expiration = datetime.datetime.now() + datetime.timedelta(30) # Post expires 30 days from now
	new_listing.post_status = "active"
	new_listing.asking_price = request.form["price"] # FORM
	new_listing.latitude = request.form["latitude"] # FORM
	new_listing.longitude = request.form["longitude"] # FORM
	new_listing.additional_text = request.form["comments"] # FORM
	new_listing.user_id = g.user

	# model.session.add(new_listing)
	# model.session.commit()
	flash("Your listing has been created.") 

	return str(new_listing.bike_id)

@app.route("/seebike/<int:id>")
def see_bike(id):
	bike = db.session.query(Bike).get(id)
	return bike.title

@app.route("/listing/<int:bike_id>") 
def listing_success(bike_id):
	# Use bike_id to get listing
	listing = db.session.query(Listing).filter(Listing.bike_id == bike_id, Listing.post_status=="Active").one()
	# Get user from listing
	user = db.session.query(User).filter_by(id=listing.user_id).one()
	# Use bike_id to get bike
	bike = db.session.query(Bike).get(bike_id)
	return render_template("listing.html", bike=bike, user=user, listing=listing)

@app.route("/mylistings")
def my_listings():
	user = flask_session['user']
	query = db.session.query(Listing, Bike).filter(Listing.bike_id == Bike.id, Listing.post_status=="Active")
	user_listings = query.filter(Listing.user_id == user).filter(Bike.user_id == user).all()

	listings = []

	# Building objects for template
	for listing, bike in user_listings:
		listings.append({'url': "/listing/" + str(bike.id),
						 'photo': bike.photo,
						 'price': listing.asking_price,
						 'title': bike.title,
						 'date': listing.post_date})

	return render_template('mylistings.html', listings=listings)


@app.route("/account")
def account():
	return "Individual account page will be here. Edit/delete listings, add new bikes, etc."
	# return render_template("account.html")

