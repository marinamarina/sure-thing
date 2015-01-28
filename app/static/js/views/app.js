define(['headroom1', 'headroom'],
	function(headroom) {
		//connect to the socket server.
    	var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
        var navMessages = $('#navMessages');

	return {

        init: function(classie) { 
            
            var bodyEl = document.body,
                content = document.querySelector( '.content-wrap' ),
                openbtn = document.getElementById( 'open-button' ),
                closebtn = document.getElementById( 'close-button' ),
                isOpen = false;

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

            openbtn.addEventListener( 'click', toggleMenu );

            if( closebtn ) {
                closebtn.addEventListener( 'click', toggleMenu );
            }

            // close the menu element if the target it´s not the menu element or one of its descendants..
            content.addEventListener( 'click', function(ev) {
                var target = ev.target;
                if( isOpen && target !== openbtn ) {
                    toggleMenu();
                }
            });    

            function toggleMenu() {
                if( isOpen ) {
                    classie.remove( bodyEl, 'show-menu' );
                    console.log('clicked')
                    $(openbtn).show();
                } else {
                    classie.add( bodyEl, 'show-menu' );
                    $(openbtn).delay(200).hide();
                }
                isOpen = !isOpen;
            }


    		//no more new messages found for this user
    		socket.on('no_new_messages', function(msg) {
        		navMessages.removeClass('orange');
    		});
                
        }//end of init
    }
});  