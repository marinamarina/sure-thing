define(['headroom1', 'headroom', 'cookie', 'bootstrap'],
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
                isOpen = false,
                played_matches_cooks = $.cookie("show_played_matches"),
                unplayedButton = $("#upcoming-past-nav li.unplayed");
                playedButton = $("#upcoming-past-nav li.played");

    		window.setTimeout(function() {
				$(".alert").fadeTo(200, 0)
    	       			   .slideUp(200, function(){
    				$(this).remove(); 
					});
				}, 1000);

 			
            /* Making room for the content of the page */
			$(".headroom").headroom({
    			"tolerance": 20,
    			"offset": 50,
    			"classes": {
        			"initial": "animated",
        			"pinned": "slideDown",
        			"unpinned": "slideUp"
    			}
    		});
            $('ul.tabs li').click(function(){
                var tab_id = $(this).attr('data-tab');

                $('ul.tabs li').removeClass('current');
                $('.tab-content').removeClass('current');

                $(this).addClass('current');
                $("#"+tab_id).addClass('current');
            })

  
            if (played_matches_cooks == 1) {
                unplayedButton
                .removeClass("active")
                .siblings()
                .addClass("active")
            } else {
                playedButton    
                .removeClass("active")
                .siblings()
                .addClass("active")
            }
            /*allCookies = document.cookie;
            console.log(allCookies.getItem('showed_played_matches').split('=')[1])*/

            $("#upcoming-past-nav li").click(function(){
                $(".active").removeClass("active");
                $(this).addClass("active");
            });

            if (openbtn) {
                openbtn.addEventListener( 'click', toggleMenu );
            }

            if( closebtn ) {
                closebtn.addEventListener( 'click', toggleMenu );
            }

            // close the menu element if the target it´s not the menu element or one of its descendants..
            if (!content == null) {
                content.addEventListener( 'click', function(ev) {
                    var target = ev.target;
                    if( isOpen && target !== openbtn ) {
                        toggleMenu();
                    }
                });  
            }  

            function toggleMenu() {
                if( isOpen ) {
                    classie.remove( bodyEl, 'show-menu' );
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