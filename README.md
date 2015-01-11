BikeList
--------

**Live Demo**

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

Create a virtual environment 

```
> virtualenv env
> source env/bin/activate
```

Install the dependencies

```
> pip install -r requirements
```

Run the app 

```
> python app.py
```

Open your browser and navigate to 

```
http://localhost:5000/
```

Note: The login functionality requires that you have a Facebook app id and secret set as local environment variables:

```
FACEBOOK_APP_SECRET
FACEBOOK_APP_ID
```