import json

from flask import Flask, render_template, redirect, request, flash, url_for, g
from flask import session as flask_session
import model

app = Flask(__name__)

app.secret_key = 'abc123321cba'


@app.route("/")
def index():
	return render_template("getbike.html")

@app.route("/addbike", methods=['POST'])
def add_bike():
	""" Takes bike object from BikeIndex API and adds bike info to db"""
	# bike = bike["name"]

	bikedata = request.form.get("bike")
	bike = json.loads(bikedata)

	print bike, " We have python success!"

	return "hello"

if __name__== "__main__":
	app.run(debug = True)