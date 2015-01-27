window.App.modules["my-favorites"] = function(config){

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
