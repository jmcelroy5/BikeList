window.App.modules["search-page"] = function(config){

	// Application state

	SearchState = {
		query: {
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
			currentPage: 0
		},
		serialize: function(){
			var str = [];
			var params = this.query;
			for(var p in params) {
				if (params.hasOwnProperty(p)) {
					str.push(encodeURIComponent(p) + "=" + encodeURIComponent(params[p]));
				}
			}
			return str.join("&");
		},
		get: function(key) {
			return this.query[key];
		},
		set: function(key,value){
			this.query[key] = value;
		}
	};

	var results = {
		listings: [],
		numResults: null,
		pageLower: null,
		pageUpper: null,
		totalResults: null,
	};

	function fetchResults(callback){
		// fetches the bikes for current searchParameters
		// once it has that data, calls callback function
		$.get('/getbikes', SearchState.serialize(), callback);
	}

	function updateResults(data){
		var response = data["response"];
		results.listings = new ListingCollection(response.listings);
		results.numResults = response["num_results"];  		// length of listings array
		results.pageLower = response["page_range_lower"];	// lower bound of items to display
		results.pageUpper = response["page_range_upper"];	// upper bound of items to display
		results.totalResults = response["total_results"];	// total number of results found for query
		results.favorites = response["favorites"];

		// trigger results-update so search panel, pagination, and listings update
		events.trigger('results-update', SearchState.query.currentPage);
	}

	events.on('parameter-update', function() {
		fetchResults(function(data){
			updateResults(data);
		});
	});

	// Models

	var ListingModel = Backbone.Model.extend({
		defaults: {
			url: '',
			latitude: null,
			longitude: null,
			id: null,
			photo: '',
			price: null,
			material: '',
			title: ''
		}
	});

	var ListingCollection = Backbone.Collection.extend({
		model: ListingModel,
		query: SearchState.serialize(), // query (searchParams) sent to the server to limit results
		url: function(){
			return "/getbikes?" + this.query;
		},
		comparator: function(listing){
			return listing.get("price");
		}
	});

	var User = Backbone.Model.extend({
		defaults: {
			id: null,
			avatar: null,
			name: null,
			favorites: []
		},
		url: '/getuser'
	});

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

		events.on('map-search-change', function(){
			this.placeMarkers();
		}.bind(this));

		// User can choose whether they want map move to trigger search
		$("#limit-map-search input:checkbox").change(function(){
			if ($(this).is(':checked')){
				window.map.enableMapSearch();
				events.trigger('map-search-change');
			}
			else{
				window.map.disableMapSearch();
				events.trigger('map-search-change');
			}
		});
	}

	Map.prototype.getViewCoords = function(){
		SearchState.set('latitudeMin', this.map.getBounds().getSouth());
		SearchState.set('latitudeMax', this.map.getBounds().getNorth());
		SearchState.set('longitudeMin', this.map.getBounds().getWest());
		SearchState.set('longitudeMax', this.map.getBounds().getEast());
		SearchState.set('currentPage', 0);
		events.trigger('parameter-update');
	};

	Map.prototype.enableMapSearch = function(){
		this.map.on('dragend', this.getViewCoords.bind(this));
		this.map.on('zoomend', this.getViewCoords.bind(this));
		SearchState.set("searchOnMapMove",true);
	};

	Map.prototype.disableMapSearch = function(){
		this.map.off('dragend');
		this.map.off('zoomend');
		SearchState.set('latitudeMin', null);
		SearchState.set('latitudeMax', null);
		SearchState.set('longitudeMin', null);
		SearchState.set('longitudeMax', null);
		SearchState.set("searchOnMapMove", false);
	};

	Map.prototype.initialize = function() {
		//Connect to MapBox API
		L.mapbox.accessToken = "pk.eyJ1Ijoiam1jZWxyb3kiLCJhIjoiVVg5eHZldyJ9.FFzKtamuKHb_8_b_6fAOFg";

		// Initialize map 
		this.map = L.mapbox.map(this.el, 'asdv.ka97lo0j', { zoomControl: false });

		// // Set starting view/zoom(SF)
		// this.map.setView([37.78, -122.44], 13);

		// Set zoom control location
		new L.Control.Zoom({ position: 'bottomleft' }).addTo(this.map);
		// Add geocoder search bar
		this.map.addControl(L.mapbox.geocoderControl('mapbox.places-v1'));
	};

	Map.prototype.placeMarkers = function(){

		var listings = results.listings;

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
		// list to hold the marker geojson models
		this.geoJson = [];

		listings.each(function(listing, idx){
			// Define geoJSON for marker and push to geojson list
			map.geoJson.push({
				type: 'Feature',
				geometry: {
					type: "Point",
					coordinates: [listing.get("longitude"), listing.get("latitude")]
				},
				properties: {
					'title': listing.get("title"),
					'image': listing.get("photo"),
					'url': listing.get("url"),
					'marker-size': 'large',
					'marker-color': '#00529f',
					'marker-symbol': 'bicycle',
				}
			});

			map.markerMap[listing.id] = idx;
		});

		// Add them all to the map 
		this.markerLayer.setGeoJSON(this.geoJson);
		this.markerLayer.addTo(this.map);

		// fit map bounds to markers if "search on map move" not selected
		if (!SearchState.get("searchOnMapMove") && listings.length){
			this.map.fitBounds(this.markerLayer.getBounds());
		}
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
	var include = function(arr,obj) {
		return (arr.indexOf(obj) != -1);
	};

	// escape user input for display
	var escapeHTML = function(html) {
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

		// TODO: Show loading indicator while results are being fetched

		events.on('results-update', function() {
			var $searchResults = $('#search-results');
			$searchResults.empty();

			// Get the updated search results
			var listings = results.listings;

			if (listings.length < 1){
				$searchResults.html("<h4>No bikes found. Expand your search and try again.</h4>");
			}

			// Loop through listings in response object
			listings.each(function(listing){

				// TODO: replace this JQuery mess with rendering a template

				var $titleLink = $("<a />",{
					"href": listing.get("url"),
					"text": listing.get("title")
				});
				
				var $photoLink = $("<a />",{
					"href": listing.get("url")
				});

				var $bikePhoto = $("<div />", {
					"class": "img",
					"html": "<div class='pricetag'>  $" + escapeHTML(listing.get("price")) + "</div>",
					"style": 'background-image:url("' + listing.get("photo") + '")'
				});

				$photoLink.append($bikePhoto);

				var $li = $("<li />",{
					"class": "listing-link",
					"data-id": listing.get("id")
				});

				$li.append($photoLink, $titleLink);

				if (currentUser["id"]) {
					var favorites = currentUser.get("favorites");
					var $heartIcon = $("<i class='heart fa fa-heart-o' data-id='" + listing.id + "'></i>");
					if (favorites && include(favorites, listing.id)){
						$heartIcon.removeClass("fa-heart-o");
						$heartIcon.addClass("fa-heart");
					}
					$li.append($heartIcon);
				}
				$searchResults.append($li);
			});

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
			var page = SearchState.get('currentPage');
			if (page > 0){
				SearchState.set('currentPage', page - 1);
			}
			$('html, body').animate({
				scrollTop: ($('#search-results').offset().top - 125)
			},500);
			events.trigger('parameter-update');
		});

		$(next).on('click', function(){
			var page = SearchState.get('currentPage');
			SearchState.set('currentPage', page + 1);
			$('html, body').animate({
				scrollTop: ($('#search-results').offset().top - 125)
			},500);
			events.trigger('parameter-update');
		});

		events.on('results-update', function(currentPage){
			$(lower).html(results["pageLower"]);
			$(upper).html(results["pageUpper"]);
			$(total).html(results["totalResults"]);

			if (results.listings.length < 1){
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

		$('#filter-submit').on('click', function(e){

			e.preventDefault();

			var sizeList = [];
			// get checked sizes from form
			$('#size-filters input:checked').each(function(i,size){
				sizeList.push($(size).attr('name'));
			});
			SearchState.set('sizes', sizeList);

			var materialList = [];
			// get checked materials from form
			$('#materials-filters input:checked').each(function(i,material){
				materialList.push($(material).attr('name'));
			});
			SearchState.set('materials', materialList);

			// get min price from slider
			var minPriceValue = $('#range').val()[0];
			SearchState.set('minPrice', minPriceValue);

			// get max price from slider
			var maxPriceValue = $('#range').val()[1];
			SearchState.set('maxPrice', maxPriceValue);

			// get checked handlebars from slider
			var handlebarList = [];
			$('#handlebar-filters input:checked').each(function(i,handlebar){
				handlebarList.push($(handlebar).attr('name'));
			});
			SearchState.set('handlebars', handlebarList);
			
			// reset page to 0
			SearchState.set('currentPage',0);

			// triggers results-update which triggers map/listings update
			events.trigger('parameter-update');

			// triggers url hash update
			events.trigger('filter-update');
		});

		$('#filter-clear').on('click', function(e){
			e.preventDefault();
			// reset price slider
			$("#range").val([0, 1500]);
			// reset checked fields
			$("input:checked").removeAttr('checked');
			// reset search parameters
			SearchState.set("sizes", []);
			SearchState.set("materials", []);
			SearchState.set("handlebars", []);
			SearchState.set("maxPrice", null);
			SearchState.set("minPrice", null);
			SearchState.set("currentPage", 0);
			events.trigger("parameter-update");
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

	// TODO: function that saves search parameters to URL

	// "Controller"

	$(document).ready(function(){
		// fetch current user
		currentUser = new User();
		currentUser.fetch();

		// initial search results fetch
		fetchResults(function(data){
			updateResults(data);
		});

		// instantiate the views
		window.map = new Map(document.querySelector('#map-panel'));
		new Listings(document.querySelector('#search-results'));
		new Paginator(document.querySelector('#paginator'));
		new Filters(document.querySelector('#search-filters'));
	});
};

