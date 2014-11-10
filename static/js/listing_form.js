// IIFE, Immediately Invoked Function Expression
(function() {
	var map; 
	var geocoder;

	function initialize() {
		geocoder = new google.maps.Geocoder();
		var startCenter = new google.maps.LatLng(37.77343, -122.442565);
		var mapOptions = {
			zoom: 12,
			center: startCenter
		};
		map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
	}

	google.maps.event.addDomListener(window, 'load', initialize);

	$("#location").on("blur",function(e){
			var location = document.getElementById("location").value;
			placeMarker(location);
	});

	$("#listing-form").on("submit", function(e){
		// Send marker coordinates for location instead of form field value
		e.preventDefault();
		var price = document.getElementById("price").value;
		var comments = document.getElementById("comments").value;
		var latitude = marker.position["k"];
		var longitude = marker.position["B"];

		// AJAX post to add listing to database
		$.post("/addlisting", {
			price: price,
			comments: comments,
			latitude: latitude,
			longitude: longitude
			},
			function(response){ // server response returns bike_id
				window.location.href = "/listing/" + response;
			});
		});

	var marker;

	function placeMarker(location){
		geocoder.geocode( {address: location}, function(results){
			latLong = results[0].geometry.location;
			map.setCenter(latLong);

			// If there is already a marker, delete it
			if (marker){
				marker.setMap(null);
				marker = null;
			}

			// create new marker
			marker = new google.maps.Marker({
				position: latLong,
				map: map,
			});
		});
	}
})();