window.App.modules["my-listings"] = function(config){

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