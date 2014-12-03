window.App = (function(){

	var App = {
		initialize: function(name, config){
			modules[name](config);
		}
	};

	var modules = {};

	var events = _.clone(Backbone.Events);

	modules["my-listings"] = function(config){

		$('.delete-listing').on('click', function(e){
			listingId = $(e.currentTarget).data("id");
			events.trigger("delete-listing", listingId);
		});

		events.on("delete-listing", function(listingId){
			$('#delete-modal').modal('show');
			$(".confirm-delete").on('click', function(e) {
				$.post("/deletelisting", {listingId:listingId}, function(){
					$("#delete-modal .modal-body").html("<h3>Listing deleted.</h3><br><h4 style='color:black'>If you sold your bike, remember to transfer ownership to the new owner on BikeIndex!</h4>");
					$(".confirm-delete").hide();
					$(".cancel").text("OK").on('click', function(){
						window.location.reload();
					});
				});
			});
		});
	};

	modules["my-favorites"] = function(config){

		$('.remove-favorite').on('click', function(e){
			listingId = $(e.currentTarget).data("id");
			events.trigger("remove-favorite", listingId);
		});

		events.on("remove-favorite", function(listingId){
			$.post("/favorite", {listing:listingId}, function(){
				window.location.reload();
			});
		});
	};

	modules["active-listing"] = function(config){

		$("#back-to-search").on("click", function(e){
			e.preventDefault();
			history.back();
			console.log("history backin it up");
		});

		var bikeLocationMap = function(){
			//Connect to MapBox API
			L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";
			// Initiate map 
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

	modules["listing-form"] = function(config){

		var initializeMap = function(){
			//Connect to MapBox API
			L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";
			// Initiate map and set view
			map = L.mapbox.map('mapbox', 'examples.map-i86nkdio');
			// set starting view/zoom(SF)
			map.setView([37.79, -122.41], 10);
		};

		initializeMap();

		geocoder = new google.maps.Geocoder();

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

		markerList = [];

		var placeMarker = function(location) {
			geocoder.geocode({address:location}, function(results){
			latitude = results[0].geometry.location["k"];
			longitude = results[0].geometry.location["B"];

			map.setView([latitude, longitude], 14);

			// If there is already a marker, delete it
			if (typeof markerLayer !== 'undefined'){
				markerLayer.clearLayers();
			}

			markerList = [];

			// Create new marker/layer
			newMarker = L.mapbox.featureLayer();

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

	modules["search-page"] = function(config){

		// set defaults search params
		searchParameters = {
			sizes: [],
			materials: [],
			handlebars: [],
			maxPrice: 1500,
			minPrice: 0,

			latitudeMin: null,
			latitudeMax: null,
			longitudeMin: null,
			longitudeMax: null,

			searchOnMapMove: false,

			resultLimit: 15,
			currentPage: 0,
		};

		var currentUser = {
			id: null,
			avatar: null,
			name: null,
			favorites: []
		};

		$.get('/getuser', function(data){
			currentUser.id = data.user;
			currentUser.avatar = data.avatar;
			currentUser.name = data.name;
			currentUser.favorites = data.favorites;
		});

		function getParameter(key){
			return searchParameters[key];
		}

		function setParameter(key, value){
			searchParameters[key] = value;
			// events.trigger('parameter-update');
		}

		var results = {
			results: [],
			numResults: null,
			pageLower: null,
			pageUpper: null,
			totalResults: null,
		};

		// Views

		function Map(el) {
			this.el = el;

			this.initialize();

			events.on('results-update', function() {
				// Clear any markers that are on map 
				if (typeof this.markerLayer !== 'undefined'){
					this.markerLayer.clearLayers();
				}
				// Place new markers
				this.placeMarkers(results);
			}.bind(this));

			events.on('listing-mouse-in', function(listingId) {
				this.setMarkerActive(listingId);
			}.bind(this));
			// Another way: events.on('listing-mouse-in', this.setMarkerActive.bind(this));

			events.on('listing-mouse-out', function(listingId) {
				this.setMarkerInactive(listingId);
			}.bind(this));
			// Another way: events.on('listing-mouse-out', this.setMarkerInactive.bind(this));

			// User can choose whether they want map move to trigger search
			$("#limit-map-search input:checkbox").change(function(){
				if ($(this).is(':checked')){
					window.map.enableMapSearch();
				}
				else{
					window.map.disableMapSearch();
				}
			});
		}

		Map.prototype.getViewCoords = function(){
			setParameter('latitudeMin', this.map.getBounds().getSouth());
			setParameter('latitudeMax', this.map.getBounds().getNorth());
			setParameter('longitudeMin', this.map.getBounds().getWest());
			setParameter('longitudeMax', this.map.getBounds().getEast());
			setParameter('currentPage', 0);
			events.trigger('parameter-update');
		};

		Map.prototype.enableMapSearch = function(){
			this.map.on('dragend', this.getViewCoords.bind(this));
			this.map.on('zoomend', this.getViewCoords.bind(this));
			setParameter("searchOnMapMove",true);
			events.trigger('parameter-update');
		};

		Map.prototype.disableMapSearch = function(){
			this.map.off('dragend');
			this.map.off('zoomend');
			setParameter('latitudeMin', null);
			setParameter('latitudeMax', null);
			setParameter('longitudeMin', null);
			setParameter('longitudeMax', null);
			setParameter("searchOnMapMove", false);
			events.trigger('parameter-update');
		};

		Map.prototype.initialize = function() {
			//Connect to MapBox API
			L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";

			// Initialize map 
			this.map = L.mapbox.map(this.el, 'asdv.ka97lo0j', { zoomControl: false });

			// // Set starting view/zoom(SF)
			this.map.setView([37.78, -122.44], 13);

			// Set zoom control location
			new L.Control.Zoom({ position: 'bottomleft' }).addTo(this.map);
			// Add geocoder search bar
			this.map.addControl(L.mapbox.geocoderControl('mapbox.places-v1'));
		};

		Map.prototype.placeMarkers = function(results){

			var listings = results["results"];

			this.geoJson = [];

			this.markerLayer = L.mapbox.featureLayer();

			// Defining custom HTML for the popups
			this.markerLayer.on('layeradd', function(e){
				var marker = e.layer;
				var photo = marker.feature.properties.image;
				var url = marker.feature.properties.url;
				var popupContent = '<div class="marker-popup"><a href="' + url + '">' +
									marker.feature.properties.title + '</a><br>' +
									'<img src="' + photo + '"></div>';
				marker.bindPopup(popupContent);
			});

			// object that will be used to map listing cards to their map marker
			this.markerMap = {};

			for (var i = 0; i < listings.length; i++){

				//Current listing
				var listing = listings[i];

				// Define geoJSON for marker and push to geojson list
				this.geoJson.push({
					type: 'Feature',
					geometry: {
						type: "Point",
						coordinates: [listing.longitude, listing.latitude]
					},
					properties: {
						'title': listing.title,
						'image': listing.photo,
						'url': listing.url,
						'marker-size': 'large',
						'marker-color': '#00529f',
						'marker-symbol': 'bicycle',
					}
				});

				this.markerMap[listing.id] = i;
			}

			// Add them all to the map 
			this.markerLayer.setGeoJSON(this.geoJson);
			this.markerLayer.addTo(this.map);

			// debugger;
			// // fit map bounds to markers if "search on map move" not selected
			if (!searchParameters.searchOnMapMove && listings.length){
				this.map.fitBounds(this.markerLayer.getBounds());
				setParameter('latitudeMin', this.map.getBounds().getSouth());
				setParameter('latitudeMax', this.map.getBounds().getNorth());
				setParameter('longitudeMin', this.map.getBounds().getWest());
				setParameter('longitudeMax', this.map.getBounds().getEast());
			}
			// else if (listings.length){
			// 	// set view to marker layer one time, not dynamically
			// 	markerLayerCenter = [this.markerLayer.getBounds().getCenter().lat, this.markerLayer.getBounds().getCenter().lng];
			// 	this.map.setView(markerLayerCenter, 11);
			// }
		};

		Map.prototype.setMarkerActive = function(listingId){
			var idx = this.markerMap[listingId];
			this.geoJson[idx].properties["marker-color"] = "#82c2ee";
			this.markerLayer.setGeoJSON(this.geoJson);
			this.markerLayer.addTo(this.map);
		};

		Map.prototype.setMarkerInactive = function(listingId){
			var idx = this.markerMap[listingId];
			this.geoJson[idx].properties["marker-color"] = "#00529f";
			this.markerLayer.setGeoJSON(this.geoJson);
			this.markerLayer.addTo(this.map);
		};

		// find out if an item is in a given array
		include = function(arr,obj) {
			return (arr.indexOf(obj) != -1);
		};

		// escape user input for display
		escapeHTML = function(html) {
		return String(html)
			.replace(/&/g, '&amp;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/'/g, '&#x27;')
			.replace(/`/g, '&#x60;');
		};

		function Listings(el) {

			// events.on('parameter-update', function(){
			// 	// Show loading indicator in searchpanel while results are being fetched
			// });

			events.on('results-update', function() {
				$searchResults = $('#search-results');
				$searchResults.empty();

				// Get the updated search results
				listings = results["results"];

				if (listings.length < 1){
					$searchResults.html("<h4>No bikes found. Expand your search and try again.</h4>");
				}

				// Loop through listings in response object
				for (var i = 0; i < listings.length; i++){

					// Current listing
					var listing = listings[i];

					// Create JQuery object for listing title/link
					var $listingLink = $("<a />",{
						href: listing.url,
						text: listing.title
					});
					
					// Create JQuery object for bike photo	
					var $bikePhoto = $("<div class='img'>");
					$bikePhoto.attr('style','background-image:url("' + listing.photo + '");');
					$bikePhoto.html("<div class='pricetag'>  $" + escapeHTML(listing.price) + "</div>");
					
					var $li = $("<li class='listing-link' data-id='"+ listing.id + "' >");
					$li.append($bikePhoto, $listingLink);

					if (currentUser["id"]) {
						var $heartIcon = $("<i class='heart fa fa-heart-o' data-id='" + listing.id + "'></i>");
						if (currentUser.favorites && include(currentUser.favorites, listing.id)){
							$heartIcon.removeClass("fa-heart-o");
							$heartIcon.addClass("fa-heart");
						}
						$li.append($heartIcon);
					}

					$searchResults.append($li);
				}

				// Triggers marker color change when hovering over listing
				$(".listing-link")
					.on('mouseover', function(){
						var listingId = $(this).data('id');
						events.trigger('listing-mouse-in', listingId);
					})
					.on('mouseout', function(){
						var listingId = $(this).data('id');
						events.trigger('listing-mouse-out', listingId);
					});

				// Adds click listener to hearts and toggles favorite
				$(".heart").on('click', function(){
					var listingId = $(this).data('id');
					$(this).toggleClass("fa-heart-o fa-heart");
					$.post("/favorite", {listing: listingId});
				});
			});

		}

		function Paginator(el){
			var prev = el.querySelector('#prev');
			var next = el.querySelector('#next');
			var lower = el.querySelector('#low');
			var upper = el.querySelector('#high');
			var total = el.querySelector('#total');

			// add event listeners to buttons
			$(prev).on('click', function(){
				var page = getParameter('currentPage');
				if (page > 0){
					setParameter('currentPage', page - 1);
				}
				$('html, body').animate({
					scrollTop: ($('#search-results').offset().top - 125)
				},500);
				events.trigger('parameter-update');
			});

			$(next).on('click', function(){
				var page = getParameter('currentPage');
				setParameter('currentPage', page + 1);
				$('html, body').animate({
					scrollTop: ($('#search-results').offset().top - 125)
				},500);
				events.trigger('parameter-update');
			});

			events.on('results-update', function(currentPage){
				$(lower).html(results["pageLower"]);
				$(upper).html(results["pageUpper"]);
				$(total).html(results["totalResults"]);

				if (results.results.length < 1){
					$("#paginator").hide();
				}
				else{
					$("#paginator").show();
				}

				// hides prev button on first page
				if (currentPage === 0){
					$(prev).addClass("invisible");
					$(".glyphicon-arrow-left").addClass("invisible");
				}
				// shows prev button when page > 1
				if (currentPage > 0){
					$(prev).removeClass("invisible");
					$(".glyphicon-arrow-left").removeClass("invisible");
				}
				// shows next button when not on last page
				if (results["pageUpper"] < results["totalResults"]){
					$(next).removeClass("invisible");
					$(".glyphicon-arrow-right").removeClass("invisible");
				}
				// hides next button on last page
				if (results["pageUpper"] === results["totalResults"]){
					$(next).addClass("invisible");
					$(".glyphicon-arrow-right").addClass("invisible");
				}
			});
		}

		function Filters(el){

			// event triggered after app reads query string on page load
			events.on("set-filter-knobs", function() {
				// set filter knobs according to current searchParams
				// sizes checkboxes
				for (var a=0; a < searchParameters.sizes.length; a++){
					$('#size-filters input[name="' + searchParameters.sizes[a] + '"]').prop('checked', true);
				}
				// materials checkboxes
				for (var b=0; b < searchParameters.materials.length; b++){
					$('#materials-filters input[name="' + searchParameters.materials[b] + '"]').prop('checked', true);
				}
				for (var c=0; c < searchParameters.handlebars.length; c++){
					$('#handlebar-filters input[name="' + searchParameters.handlebars[c] + '"]').prop('checked', true);
				}
				// max/min price on slider
				$("#range").val([searchParameters.minPrice, searchParameters.maxPrice]);
			});

			$('#filter-submit').on('click', function(e){

				e.preventDefault();

				// var currentFilters = {}

				// get checked sizes from form
				var sizeList = [];
				$('#size-filters input:checked').each(function(i,size){
					sizeList.push($(size).attr('name'));
				});
				setParameter('sizes', sizeList);
				// currentFilters.sizeList = sizeList;

				// get checked materials from form
				var materialList = [];
				$('#materials-filters input:checked').each(function(i,material){
					materialList.push($(material).attr('name'));
				});
				setParameter('materials', materialList);
				// currentFilters.materials = materialList;

				// get min price from slider
				minPriceValue = $('#range').val()[0];
				setParameter('minPrice', minPriceValue);
				// currentFilters.minPrice = minPriceValue;

				// get max price from slider
				maxPriceValue = $('#range').val()[1];
				setParameter('maxPrice', maxPriceValue);
				// currentFilters.maxPrice = maxPriceValue;

				// get checked handlebars 
				var handlebarList = []
				$('#handlebar-filters input:checked').each(function(i,handlebar){
					handlebarList.push($(handlebar).attr('name'));
				});
				setParameter('handlebars', handlebarList);
				// currentFilters.maxPrice = handlebarList;

				// reset page to 0
				setParameter('currentPage', 0);
				// currentFilters.currentPage = 0;

				// triggers results-update which triggers map/listings update
				events.trigger('parameter-update');
			});

			$('#filter-clear').on('click', function(e){
				e.preventDefault();
				// reset price slider
				$("#range").val([0, 1500]);
				// reset checked fields
				$("input:checked").removeAttr('checked');
				// reset search parameters
				setParameter("sizes", []);
				setParameter("materials", []);
				setParameter("handlebars", []);
				setParameter("maxPrice", null);
				setParameter("minPrice", null);
				setParameter("currentPage", 0);
				events.trigger("parameter-update");

				var hashString = "?" + hashSearch(searchParameters);
				history.replaceState(null, null, hashString);
				history.pushState(null,null, hashString);
			});

			// Price Slider JQuery plugin
			$('#range').noUiSlider({
				start: [0,1500],
				step: 50,
				margin: 20,
				connect: true,
				direction: 'ltr',
				orientation: 'horizontal',
			
				behaviour: 'tap-drag',
				
				format: wNumb({
					mark: '.',
					decimals: 2,
					thousand: ','
				}),
				range: {
					'min': [0],
					'max': [1500]
				}
			});

			// Write price filter values to the min/max value spans
			$('#range').Link('lower').to($('#value-low'), 'html');
			$('#range').Link('upper').to($('#value-high'), 'html');
		}

		// used to set search string in URL when search filters are updated
		// make this a method of Filters prototype?
		var hashSearch = function(obj){
			return _.pairs(obj) // object to key/value pairs then to standard search query format
			.map(function(array){
				return array[0] + '=' + array[1];
			})
			.reduce(function(a,b){
				return a + '&' + b;
			});
		};
		

		// Runs on page load 
		$(document).ready(function(){

			window.map = new Map(document.querySelector('#map-panel'));
			new Listings(document.querySelector('#search-results'));
			new Paginator(document.querySelector('#paginator'));
			new Filters(document.querySelector('#search-filters'));

			// getQueryParams.js parses query string
			getQueryParams = function(queryString) {
				var query = (queryString || window.location.search).substring(1);
				if (!query) {
					return false;
				}
				return _
					.chain(query.split('&'))
					.map(function(params) {
						var p = params.split('=');
						return [p[0], decodeURIComponent(p[1])];
					})
					.object()
					.value();
			};

			function fetchResults(callback){
				$.get('/getbikes', searchParameters, callback);
				// fetches the bikes for current searchParameters
				// once it has that data, calls callback function
			}

			events.on('parameter-update', function() {
				fetchResults(function(data){
					console.log("returning results with these search filters ", searchParameters)

					updateResults(data);
				});
				// updates url search string	
				var hashString = "?" + hashSearch(searchParameters);
				history.replaceState(null, null, hashString);
			});

			function updateResults(data){
				var response = data["response"];
				results.results = response["listings"]; // array of listings
				results.numResults = response["num_results"];  // length of listings array
				results.pageLower = response["page_range_lower"]; // lower bound of items to display
				results.pageUpper = response["page_range_upper"]; // lower bound of items to display
				results.totalResults = response["total_results"]; // total number of results found for query
				results.favorites = response["favorites"];
				// trigger results-update so search panel, pagination, and listings update
				events.trigger('results-update', searchParameters["currentPage"]);
			}

			window.savedSearch = getQueryParams();
			// parse and set search params if there's a search string in URL
			if (savedSearch){
				searchString = getQueryParams();
				// make sure search options end up in right format
				searchParameters["searchOnMapMove"] = JSON.parse(searchString["searchOnMapMove"]);
				if (searchString["sizes"]){
					searchParameters["sizes"] = searchString["sizes"].split(',');
				}
				if (searchString["materials"]){
					searchParameters["materials"] = searchString["materials"].split(',');
				}
				if (searchString["handlebars"]){
					searchParameters["handlebars"] = searchString["handlebars"].split(',');
				}
				events.trigger("set-filter-knobs");
				debugger;
				events.trigger("parameter-update");
			}

			if(!savedSearch) {
				fetchResults(function(data){
					updateResults(data);
				});
			}
		});


	};

	// BASE TEMPLATE - LIST BIKE BUTTON

	$("#submit-serial").on("click",function(e){
		var serial = $("#bike-serial").val();
		$("#bike-serial").hide();
		$("#loading").show();
		if (serial.length < 1){
			$("#loading").hide();
			$("#bike-serial").show();
			$("#get-serial > h3").text("Please enter a valid serial number").css("color","red");
		}
		else{
			getBike(serial);
		}
	});

	function getBike(serial) {

		$.get("/fetchbike", {serial: serial}, function(data){
			// check to make sure we got one bike back from BikeIndex API
			var bike;
			if (data["response"]["bikes"].length === 1){
				bike = data["response"]["bikes"][0];
			}
			else if (data["response"]["bikes"].length != 1){
				$("#get-serial > h3").text("No bike with that serial number found. Make sure you entered your serial number exactly.").css("color","red");
				$("#bike-serial").show();
				$("#loading").hide();
				$("#get-serial").show();
				$("#submit-serial").show();
			}

			// check if bike is stolen
			if (bike && bike["stolen"] === true){
				$("#list-modal-body").html("<img src='https://bikeindex.org/assets/home/hacksaw-man.svg'>");
				$("#list-modal-body").prepend("<a href='" + bike.url + "'><h4>Notify the owner on BikeIndex</h4></a>");
				$("#list-modal-body").prepend("<h1>That bike is stolen!</h1>").css("color","red").css("text-align","center");
				$("#submit-serial").hide();
			}

			// if bike is not stolen
			if (bike && bike["stolen"] === false){
				postBike(bike);
			}
		});
	}

	function postBike(bike){
		// Turn bike object into JSON string to pass to python
		var bikedata = JSON.stringify(bike);

		$.post("/addbike", {bike: bikedata}, function(){
			$("#list-modal-body").html("<h3 style='color:#66CD00'> We found your bike on BikeIndex.</h3>").css("color","green");
			$("#submit-serial").replaceWith("<button id='continue-to-form' class='btn btn-primary'>Continue</button>");
			$("#continue-to-form").on('click', function(){
				window.location.replace("/list");
			});
		});
	}

	return App;
})();








