BikeList
--------

*** Live Demo ***

http://bikelist.herokuapp.com/

**Description**

BikeList is an alternative used bike marketplace that introduces more transparency in the bike buying process so you can rest assured that your purchase will not contribute to the cycle of bike theft. BikeList integrates with BikeIndex, an open-source bike registry, to verify that listed bikes are not stolen and uses Facebook OAuth to tie listings to the seller's online identity. A smooth user interface and features such as location-based search, bike-specific search filters, detailed bike specs, and info guides further enhance the bike buyer's experience.

### Screenshots

**Search Page**
![alt text](https://cldup.com/-CCK9vvr9h.png)

**Bike Listing Page**
![alt text](https://cldup.com/SG7KLqyY4C.png)

**Catching Stolen Bikes**
![alt text](https://cldup.com/Td9NE6eydd.png)

### Technology Stack

**Application:** Python, Flask, Jinja, SQLAlchemy, PostgreSQL
**APIs:** BikeIndex, Facebook OAuth, Mapbox.js, Google Geocoding
**Front-End**: HTML/CSS, Bootstrap, JQuery, JavaScript, Backbone 

### How to run BikeList locally

1. Create a virtual environment

<section>
	> virtualenv env
	> source env/bin/activate
</section>

2. Install the dependencies

<section>
	> pip install -r requirements
</section>

3. Run the app

<section>
	> python app.py
</section>

4. Open your browser and navigate to 

<section>
	http://localhost:5000/
</section>

Note: Login requires that you have a Facebook 