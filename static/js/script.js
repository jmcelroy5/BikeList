$("#target").on("click",function(e){
	e.preventDefault();
	var serial = $("#bike_serial").val();
	getBike(serial);
});

function getBike(serial) {

	$.get("https://bikeindex.org/api/v1/bikes?serial=" + serial, function(data){

		// check to make sure we got one bike back
		if (data["bikes"].length === 1){
			var bike = data["bikes"][0];
		}
		else {
			alert("No bike with that serial number found.");
		}

		// check that bike["stolen"] === false!
		var stolen = bike["stolen"];
		if (stolen===true){
			alert("Uh oh. Looks like we have a stolen bike on our hands.");
			// How to proceed?
		}
		if (bike && stolen===false){
			// display bike photo and specs for verification
			$("#bike-info").show();
			$("#bike-pic").attr('src', bike["photo"]);

			$("#bike-info > h1").text(bike["title"]);
			$("#serial").append(bike["serial"]);
			$("#manufacturer").append(bike["manufacturer_name"]);
			$("#model").append(bike["frame_model"]);
			$("#year").append(bike["year"]);
			$("#color").append(bike["frame_colors"][0]);
			if (bike["frame_material"]){
				$("#material").append(bike["frame_material"]["name"]);
			}
			if (bike["handlebar_type"]){
				$("#handlebar").append(bike["handlebar_type"]["name"]);
			}
			if (bike["rear_wheel_size"]){
				$("#wheel").append(bike["rear_wheel_size"]["name"]);	
			}

			// add click listeners to confirmation buttons
			$("#Yes").on("click",function(e){
				e.preventDefault();
				postBike(bike);
			});
			$("#No").on("click", function(e){
				e.preventDefault();
				alert("Oh, bummer! Check to make sure you entered your serial number correctly.");
				$("#bike-info").hide();
			});
		}
	});
}

function postBike(bike){
	// Turn bike object into JSON string to pass to python
	var bikedata = JSON.stringify(bike);

	$.post("/addbike", {bike: bikedata}, function(){
		alert("Bike added to database!");	// or flash message in flask
		window.location.replace("/listing");
	});
}

	