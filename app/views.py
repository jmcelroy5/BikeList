from flask import Blueprint, render_template, request, jsonify, g, redirect, flash, url_for
from flask import session as flask_session
from model import Bike, Listing, User
import model
from flask_oauth import OAuth
from flask.ext.login import LoginManager
from app import app, db
import os
import datetime
import json
import requests


FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': ('email, ')})

@facebook.tokengetter
def get_facebook_token():
    return flask_session.get('facebook_token')

def pop_login_session():
    flask_session.pop('logged_in', None)
    flask_session.pop('facebook_token', None)

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
		new_user.avatar = facebook.get('/me/picture?redirect=false').data
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

@app.route("/logout")
def logout():
    pop_login_session()
    flash("You are logged out.")
    return redirect('/')

@app.route("/account")
def account():
	return "Individual account page will be here. Edit/delete listings, add new bikes, etc."
	# return render_template("account.html")

@app.route('/clearsession')
def clear_session():
	flask_session['logged_in'] = None
	flask_session['facebook_token'] = None
	flask_session['BI_authorized'] = None
	flask_session['bikeindex_token'] = None
	return "Session cleared!"

@app.route('/getsession')
def get_session():
	print "\nLogged in:", flask_session.get('logged_in', 'Not set')
	print "\n Facebook token:", flask_session.get('facebook_token','Not set')
	print "\n BikeIndex authorized:", flask_session.get('BI_authorized', 'Not set')
	print "\n BikeIndex token:", flask_session.get('bikeindex_token', 'Not set')
	print "\n Current user:", flask_session.get("user", "Not set")
	return "Check the console."

# @app.route("/_get_current_user")
# def get_current_user():
# 	""" Get current user from session """
# 	return g.user






# Bike Index OAuth Stuff:

oauth2 = OAuth()

bikeindex = oauth2.remote_app('bikeindex',
    base_url='https://bikeindex.org',
    request_token_url=None,
    access_token_url='/oauth/authorize',
    authorize_url='/oauth/authorize',
    consumer_key='b000781446a184b14193ae041dae1b08b89da22e36523e44d68ab8e878a54d58',
    consumer_secret='486ca32cfa6accc24493031b44ef95b1064214def4550581411e400aa3b7c1d5',
    request_token_params={'scope': ('public'), 'response_type': 'code'})

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
	# flask_session['BI_authorized'] = True
	# flask_session['bikeindex_token'] = resp['authenticity_token']
	# return resp
	pass

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



# # Flask-Login session manager stuff

# app.config.from_object('config')

login_manager = LoginManager()
login_manager.init_app(app) 

# @login_manager.user_loader
# def load_user(id):
# 	try:
# 		return session.query(User).get(int(id))
# 	except (TypeError, ValueError):
# 		pass


# Runs on browser refresh. Checks for current user and bike
@app.before_request
def get_current_user():
    user_id = flask_session.get('user', None)
    if user_id:
    	user = db.session.query(User).filter_by(id=user_id).one()
    	g.user = user.id
    	g.avatar = user.avatar
    	g.name = user.first_name

# Make current user available on templates
@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}

@app.route("/")
def home_page():
	# Now home route just renders template and all content is generated by javascript
	return render_template("index.html")

@app.route("/get_all_bikes")
def get_all_bikes():
	""" get search results """

	materials = request.args.getlist('materials[]') 		# returns list of names of checkboxes that are checked when form submits
	print "MATERIALS=========", materials
	# materials looks like: [u'Carbon or composite', u'Aluminum']
	handlebars = request.args.getlist('handlebars[]') 		# returns list of names of checkboxes that are checked when form submits
	print "HANDLEBARS=========", handlebars
	min_price = request.args.get('min_price')
	print "MIN_PRICE=========", min_price
	max_price = request.args.get('max_price')
	print "MAX_PRICE=========", max_price

	# Base query for active listings
	query = db.session.query(Listing, Bike).filter(Listing.bike_id == Bike.id, Listing.post_status=="Active") # Base query
	# query = Listing.query.join(Bike).filter(Listing.bike_id == Bike.id, Listing.post_status=="Active")

	# Filters
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

	all_listings = query.all()	# Finish the query

	response = []

	# Building final response object
	for listing, bike in all_listings:
		response.append({'url': "/listing/" + str(bike.id),
						'latitude': listing.latitude, 
						'longitude': listing.longitude,
						'photo': bike.photo,
						'price': listing.asking_price,
						'material': bike.frame_material,
						'title': bike.manufacturer + " " + 
								 bike.frame_model + 
								" ($" + str(listing.asking_price) + ")"})

	return jsonify(response=response)
		
@app.route("/sell")
def index():
	return render_template("getbike.html")

@app.route("/fetchbike")
def fetch_bike():
	serial = request.args.get("serial")
	params = {"serial":serial}
	r = requests.get("https://bikeindex.org/api/v1/bikes", params=params)
	bike = r.json()
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

@app.route("/listing/<int:id>") 
def listing_success(id):
	bike = db.session.query(Bike).get(id)
	return render_template("listing.html", bike=bike)

