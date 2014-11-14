	L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";

	var map = L.mapbox.map('map-panel', 'examples.map-i86nkdio');
	map.setView([37.79, -122.41], 14);

	$.get('/get_all_bikes', function(response){
			for (i=0; i<response.length; i++){
				var bike = response[i]['bike'];
				var listing = response[i]['listing'];

				// Add marker with photo and listing data 
				L.mapbox.featureLayer({
		    		type: 'Feature',
		    		geometry: {
		        		type: 'Point',
			        	coordinates: [listing.longitude, listing.latitude]
			    	},
			    	properties: {
				        title: bike.title,
				        // description: "blah blah",
				        'marker-size': 'medium',
				        'marker-color': '#FF6699',
				        'marker-symbol': 'bicycle'
			   		}
				}).addTo(map);
			}
		}
	});