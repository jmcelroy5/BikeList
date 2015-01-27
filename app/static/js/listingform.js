window.App.modules["listing-form"] = function(config){

	var initializeMap = function(){
		//Connect to MapBox API
		L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";
		// Initiate map and set view
		map = L.mapbox.map('mapbox', 'examples.map-i86nkdio');
		// set starting view/zoom(SF)
		map.setView([37.79, -122.41], 14);
	};

	initializeMap();

	var geocoder = new google.maps.Geocoder();

	$("#location").blur(function(e){
		var value = $(this).val();
		placeMarker(value);
	});

	$("#listing-form").on("submit", function(e){
		// Send marker coordinates for location instead of form field value
		e.preventDefault();
		var price = $("#price").val();
		var comments = $("#comments").val();
		var email = $("#email").val();

		// AJAX post to add listing to database
		$.post("/addlisting", {
				price: price,
				comments: comments,
				latitude: latitude,
				longitude: longitude,
				email: email
			},
			function(response){
				window.location.href = "/mylistings";
			});
		});

	var markerList = [];

	var placeMarker = function(location) {
		geocoder.geocode({address:location}, function(results){

			var latitude = results[0].geometry.location.lat();
			var longitude = results[0].geometry.location.lng();

			map.setView([latitude, longitude], 14);

			// If there is already a marker, delete it
			if (typeof markerLayer !== 'undefined'){
				markerLayer.clearLayers();
			}

			var markerList = [];

			// Create new marker/layer
			var newMarker = L.mapbox.featureLayer();

			// Marker location and properties
			var geoJson = [{
				type: 'Feature',
				geometry: {
					"type": "Point",
					"coordinates": [longitude, latitude]
				},
				properties: {
					'marker-size': 'large',
					'marker-color':  '#00529f',
					'marker-symbol': 'bicycle'
				}
			}];

			// Set geoJSON
			newMarker.setGeoJSON(geoJson);
			// Add marker to the list 
			markerList.push(newMarker);
			// so we can clear layer if user needs to place a new marker
			markerLayer = L.layerGroup(markerList);
			// and finally, add it to the map
			markerLayer.addTo(map);
		});
	};
};
