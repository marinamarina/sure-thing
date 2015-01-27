define(['headroom1', 'headroom', 'classie'],
	function(headroom, classie) {
		//connect to the socket server.
    	var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    	var navMessages = $('#navMessages');

	return {

        init: function() { 
    		window.setTimeout(function() {
				$(".alert").fadeTo(200, 0)
    	       			   .slideUp(200, function(){
    				$(this).remove(); 
					});
				}, 1000);

 				/* Making room for the menu */

				$(".headroom").headroom({
    				"tolerance": 20,
    				"offset": 50,
    				"classes": {
        				"initial": "animated",
        				"pinned": "slideDown",
        				"unpinned": "slideUp"
    				}
    			})


    			//no more new messages found for this user
    			socket.on('no_new_messages', function(msg) {
        			navMessages.removeClass('orange');
    			});
        }//end of init
    }
});  