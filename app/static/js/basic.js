$(document).ready(function () {
	console.log('baaa');

    $("#menu-toggle").click(function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("active");
        
	});
})