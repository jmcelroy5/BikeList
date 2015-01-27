window.App.modules["active-listing"] = function(config){

	var bikeLocationMap = function(){
		//Connect to MapBox API
		L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";
		// Initialize map 
		map = L.mapbox.map('bikeLocation', 'examples.map-i86nkdio');

		// get coordinates of listing 
		var longitude = config.longitude;
		var latitude = config.latitude;

		// set starting view/zoom(SF)
		map.setView([latitude, longitude], 12);
		// Create new marker/layer
		newMarker = L.mapbox.featureLayer();
		// Marker location and properties
		var geoJson = [{
			type: 'Feature',
				"geometry": {
					"type": "Point",
					"coordinates": [longitude, latitude]
				},
				"properties": {
					'marker-size': 'large',
					'marker-color':  '#00529f',
					'marker-symbol': 'bicycle'
				}
			}];
		// Set geoJSON
		newMarker.setGeoJSON(geoJson);
		newMarker.addTo(map);
	};

	bikeLocationMap();
};