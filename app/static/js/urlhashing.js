// //read URL on page load
// events.on("filter-update", function(){
// 	hashString = window.location.search;
// 	if (hashString){
// 		fetchResults(function(data){
// 			updateResults(data);
// 		});
// 	}
// 	// set search parameter object to match 
// 	// set filter knobs to match
// });

// // set URL when filters update
// function hashSearch(obj){
// 	return _.pairs(obj)
// 		.map(function(array){
// 			return array[0] + '=' + encodeURIComponent(array[1]);
// 		})
// 		.reduce(function(a,b){
// 			return a + '&' + b;
// 		});
// }

// events.on('filter-update', function(){
// 	var hashString = "?" + hashSearch(searchParameters);
// 	history.replaceState(null, null, hashString);
// });
