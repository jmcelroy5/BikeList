window.App = (function(){

	var App = {
		initialize: function(name, config){
			this.modules[name](config);
		},
		modules: {},
	};

	// event bus - intentionally global for now
	events = _.clone(Backbone.Events);

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



