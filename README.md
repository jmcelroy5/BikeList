BikeList
--------

**Description**

BikeList is an alternative used bike marketplace that introduces more transparency in the bike buying process so you can rest assured that your purchase will not contribute to the cycle of bike theft. BikeList integrates with BikeIndex, an open-source bike registry, to verify that listed bikes are not stolen and uses Facebook OAuth to tie listings to the seller's online identity. A smooth user interface and features such as location-based search, bike-specific search filters, detailed bike specs, and info guides further enhance the bike buyer's experience.

**Inspiration**

Shortly before I started Hackbright my touring bike that I had ridden thousands of miles was stolen. When I started scanning Craigslist for a new bike, it was frustrating to see so many listings that seemed suspicious. The loss of my bike was so devastating, I didn't want to buy a stolen bike and become complicit in the crime. 

In the aftermath I found out about BikeIndex, an online national bike registry that allows you to register your bike and, if the worst ever befalls, report it as stolen. The BikeIndex registry serves as a resource for used bike buyers to check a bike serial number and see if it's stolen, and the site has helped thousands of bike theft victims recover their bikes. 

Part of the purpose of BikeList is to encourage more people to register their bikes. The BikeIndex registration process is quick and easy, and the more people who register their bikes the closer we get to making bike theft a thing of the past.

**Acknowledgement**

Thank you to Seth Herr at BikeIndex for expanding the BikeIndex API response to include bike frame size.

### Screenshots

** Search Page **
![alt text](https://cldup.com/-CCK9vvr9h.png)

![alt text](https://cldup.com/Q5WMu1Zb47.png)

**Bike Listing Page**
![alt text](https://cldup.com/SG7KLqyY4C.png)

**Catching Stolen Bikes**
![alt text](https://cldup.com/Td9NE6eydd.png)

### Technology Stack

**Application:** Python, Flask, Jinja, SQLAlchemy, SQLite  
**APIs:** BikeIndex, Facebook OAuth, Mapbox.js, Google Geocoding  
**Front-End**: HTML/CSS, Bootstrap, JQuery, JavaScript, Backbone  
